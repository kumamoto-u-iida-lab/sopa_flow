#!/bin/bash
# run_span.sh — 行を緩めた配置（place_span_tbl.py）を 回路 × 4通り で回す。2026-10-05。
#   4通り = MODE(B: 行の範囲固定 / A: 辺ごとに1行の余裕) × FT(edge: 中継は子ごと / share: 親ごとに共有)
#   回路は CKTS の順（小さい順に並べておく）。各結果は check_span.py で検算する。
# 使い方:  bash run_span.sh
# 環境:    CKTS="girl10 robm ..."  MODES="B A"  FTS="edge share"  ATIME=3600  JOBS=2  THREADS=8
#          SUPERSET=structures/superset_allrelay_s125.v  CAND_RULE=now  OUT=results/place_span_s125_now
#          EBR=results/eblif_relay（無ければ insert_relay.py で作る）
# 出力:    $OUT/<回路>_<MODE>_<FT>.log と .json、最後に $OUT/summary.txt
# 並列本数の目安: 1本 3〜5GB 使う（bridge, 60秒時点）。空きメモリ(GB) ÷ 6 くらい
set -u
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=$ROOT/src
CKTS=${CKTS:-"girl10 robm bridge proc81616 v16 pp proc1688 e15 e8 e2 e4"}
MODES=${MODES:-"B A"}
FTS=${FTS:-"edge share"}
ATIME=${ATIME:-3600}
JOBS=${JOBS:-2}
THREADS=${THREADS:-8}
CAND_RULE=${CAND_RULE:-now}
SUPERSET=${SUPERSET:-structures/superset_allrelay_s125.v}
OUT=${OUT:-results/place_span_s125_$CAND_RULE}
EBR=${EBR:-results/eblif_relay}
for v in SUPERSET OUT EBR; do eval "p=\$$v"; [ "${p#/}" = "$p" ] && eval "$v=\$ROOT/\$p"; done
mkdir -p "$OUT"

if [ ! -d "$EBR" ]; then
  echo "=== 中継入り EBLIF が無いので作る: $EBR ==="
  (cd "$SRC" && D0=99 OUTDIR="$EBR" python3 insert_relay.py) || exit 1
fi

echo "構造=$SUPERSET  規則=$CAND_RULE  ATIME=$ATIME  JOBS=$JOBS  THREADS=$THREADS  出力=$OUT"
echo "回路(この順)=$CKTS  MODE=$MODES  FT=$FTS"

run_one() {   # 回路 MODE FT
  c=$1; M=$2; F=$3
  E=$EBR/$c/mapped_$c.v.eblif; L=$OUT/${c}_${M}_${F}.log
  echo "[$(date +%H:%M:%S)] 開始 $c $M $F"
  (cd "$OUT" && MODE=$M FT=$F CAND_RULE=$CAND_RULE ATIME=$ATIME THREADS=$THREADS \
      /usr/bin/time -f "メモリ最大 %MKB / 全体 %es" python3 "$SRC/place_span_tbl.py" "$E" "$SUPERSET") > "$L" 2>&1
  J=$OUT/place_span_${M}_${F}_$c.json
  if [ -f "$J" ]; then
    mv "$J" "$OUT/${c}_${M}_${F}.json"
    CAND_RULE=$CAND_RULE python3 "$SRC/check_span.py" "$E" "$SUPERSET" "$OUT/${c}_${M}_${F}.json" >> "$L" 2>&1
  fi
  echo "[$(date +%H:%M:%S)] 終了 $c $M $F: $(grep -h '^結果' "$L" | head -1)"
}
export -f run_one; export EBR OUT SRC SUPERSET CAND_RULE ATIME THREADS

for c in $CKTS; do for M in $MODES; do for F in $FTS; do echo "$c $M $F"; done; done; done \
  | xargs -P "$JOBS" -L 1 bash -c 'run_one $0 $1 $2'

{
  printf "%-10s" 回路; for M in $MODES; do for F in $FTS; do printf " | %-22s" "$M-$F"; done; done; echo
  for c in $CKTS; do
    printf "%-10s" "$c"
    for M in $MODES; do for F in $FTS; do
      L=$OUT/${c}_${M}_${F}.log
      r=$(grep -h '^結果' "$L" 2>/dev/null | head -1 | sed -E 's/^結果: ([^ ]+ \([0-9]+s\)).*/\1/')
      ck=$(grep -h '^検算' "$L" 2>/dev/null | grep -o '誤り [0-9]*')
      printf " | %-22s" "${r:-なし}${ck:+ ($ck)}"
    done; done; echo
  done
} | tee "$OUT/summary.txt"
