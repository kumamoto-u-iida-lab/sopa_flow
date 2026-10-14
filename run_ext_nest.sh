#!/bin/bash
# run_ext_nest.sh — 段固定で配置し、載らなかった回路だけ案B・子ごと（place_span_tbl.py MODE=B FT=edge）で配置し直す。2026-10-14。
#   目的: 外部入力を FF 側ほど減らした構造（先頭 n 本だけ配る入れ子、src/ext_nest.py）に small 41回路が載るか。
#   比較は同じ回し方で外部入力が全段 45本の構造（superset_r1536_alt_cyc.v）。
# 使い方:  bash run_ext_nest.sh                                          # 入れ子の構造
#          SUPERSET=structures/superset_r1536_alt_cyc.v OUT=results/place_r1536_ext45u bash run_ext_nest.sh   # 比較（全段45本）
# 環境:    SUPERSET（既定 structures/superset_r1536_alt_cyc_ext45n.v） CAND_RULE（既定 alt_cyc）
#          ATIME1（段固定の上限秒, 既定 600） ATIME2（案Bの上限秒, 既定 3600） JOBS（既定 2） THREADS（既定 8）
#          EBR（中継入り eblif, 既定 results/eblif_relay） CKTS（既定 41回路を小さい順）
# 出力:    $OUT/<回路>_fixed.log / _B.log / _B.json（案Bの配置と PI→EXT 割り当て）、最後に $OUT/summary.txt
# メモリ:  案B は 1本 3〜5GB（bridge, 60秒時点）。空きメモリ(GB) ÷ 6 くらいを JOBS に
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); SRC=$ROOT/src
SUPERSET=${SUPERSET:-structures/superset_r1536_alt_cyc_ext45n.v}
CAND_RULE=${CAND_RULE:-alt_cyc}
ATIME1=${ATIME1:-600}; ATIME2=${ATIME2:-3600}; JOBS=${JOBS:-2}; THREADS=${THREADS:-8}
EBR=${EBR:-results/eblif_relay}
OUT=${OUT:-results/place_r1536_ext45n}
for v in SUPERSET OUT EBR; do eval "p=\$$v"; [ "${p#/}" = "$p" ] && eval "$v=\$ROOT/\$p"; done
mkdir -p "$OUT"
if [ -z "${CKTS:-}" ]; then   # セル数の小さい順
  CKTS=$(for d in "$EBR"/*/; do c=$(basename "$d"); echo "$(grep -c '^.subckt cell' "$d/mapped_$c.v.eblif") $c"; done | sort -n | awk '{print $2}' | tr '\n' ' ')
fi
echo "構造=$SUPERSET  規則=$CAND_RULE  段固定 ${ATIME1}s → 案B ${ATIME2}s  JOBS=$JOBS THREADS=$THREADS  出力=$OUT"
grep -o 'N_EXT_LIST=\[[0-9, ]*\]' "$SUPERSET"

one() {
  c=$1; E=$EBR/$c/mapped_$c.v.eblif; L1=$OUT/${c}_fixed.log; L2=$OUT/${c}_B.log
  (cd "$OUT" && ATIME=$ATIME1 CAND_RULE=$CAND_RULE /usr/bin/time -f "メモリ最大 %MKB / 全体 %es" \
      python3 "$SRC/place_fixed_tbl.py" "$E" "$SUPERSET") > "$L1" 2>&1
  r1=$(grep -h '^結果' "$L1" | head -1)
  [ -f "$OUT/place_fixed_tbl_$c.json" ] && mv "$OUT/place_fixed_tbl_$c.json" "$OUT/${c}_fixed.json"
  case "$r1" in *OPTIMAL*|*FEASIBLE*) case "$r1" in *INFEASIBLE*) ;; *) echo "[$(date +%H:%M:%S)] $c 段固定: $r1"; return;; esac;; esac
  echo "[$(date +%H:%M:%S)] $c 段固定: $r1 → 案B"
  (cd "$OUT" && MODE=B FT=edge ATIME=$ATIME2 THREADS=$THREADS CAND_RULE=$CAND_RULE /usr/bin/time -f "メモリ最大 %MKB / 全体 %es" \
      python3 "$SRC/place_span_tbl.py" "$E" "$SUPERSET") > "$L2" 2>&1
  J=$OUT/place_span_B_edge_$c.json
  if [ -f "$J" ]; then
    mv "$J" "$OUT/${c}_B.json"
    CAND_RULE=$CAND_RULE python3 "$SRC/check_span.py" "$E" "$SUPERSET" "$OUT/${c}_B.json" >> "$L2" 2>&1
  fi
  echo "[$(date +%H:%M:%S)] $c 案B: $(grep -h '^結果' "$L2" | head -1)"
}
export -f one; export SRC OUT EBR SUPERSET CAND_RULE ATIME1 ATIME2 THREADS
echo $CKTS | tr ' ' '\n' | xargs -P "$JOBS" -I{} bash -c 'one {}'

{
  echo "構造=$(basename "$SUPERSET")  段固定 ${ATIME1}s / 案B ${ATIME2}s"
  printf "%-10s | %-60s | %s\n" 回路 段固定 "案B・子ごと（検算）"
  for c in $CKTS; do
    r1=$(grep -h '^結果' "$OUT/${c}_fixed.log" 2>/dev/null | head -1 | sed -E 's/^結果: //; s/  gap1=.*//')
    r2=$(grep -h '^結果' "$OUT/${c}_B.log" 2>/dev/null | head -1 | sed 's/^結果: //')
    ck=$(grep -h '^検算' "$OUT/${c}_B.log" 2>/dev/null | grep -o '誤り [0-9]*')
    printf "%-10s | %-60s | %s\n" "$c" "${r1:-なし}" "${r2:--}${ck:+ ($ck)}"
  done
  n1=$(grep -l '^結果: \(OPTIMAL\|FEASIBLE\)' "$OUT"/*_fixed.log 2>/dev/null | wc -l)
  n2=$(grep -l '^結果: \(OPTIMAL\|FEASIBLE\)' "$OUT"/*_B.log 2>/dev/null | wc -l)
  echo "載った: 段固定 $n1 + 案B $n2 = $((n1 + n2)) / $(echo $CKTS | wc -w)"
} | tee "$OUT/summary.txt"
