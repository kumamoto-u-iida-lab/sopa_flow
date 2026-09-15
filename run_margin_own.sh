#!/bin/bash
# run_margin_own.sh — 全中継の専用構造に「細くなる段（幅が前段以下の段）に +M 枠」の余白を足して配置配線（2026-09-15）
#   根拠（5回のなぜ）: 幅=セル数ちょうど（余白ゼロ）なので、FF 側の細くなる帯で前段の出力が次段の口にぴったり入り詰まる。
#   手順  ① results/eblif_relay/<回路>（中継入り、複製なし）から MARGIN=M の専用構造を生成 → results/cone_noskip_m<M>/
#         ② 段固定 CP-SAT（表制約版）で配置配線 → results/place_own_m<M>/<回路>.log, summary.csv
#   使い方: MARGINS="1 2 3" JOBS=8 ATIME=3600 ./run_margin_own.sh            （回路省略 = INFEASIBLE だった14回路）
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); SRC=$ROOT/src; RES=$ROOT/results
JOBS=${JOBS:-8}; ATIME=${ATIME:-3600}; MARGINS=${MARGINS:-"1 2 3"}
CKTS="${*:-cat checker9 indep lift lift2 lightnew pilot dmac threediff e7 e16 e2 lcu robotben}"
[ -d "$RES/eblif_relay" ] || { echo "results/eblif_relay が無い。先に: STEP=1 ./run_noskip_superset.sh"; exit 1; }
for M in $MARGINS; do
  CD=$RES/cone_noskip_m$M; OUT=$RES/place_own_m$M; mkdir -p "$OUT"
  echo "=== MARGIN=+$M: 構造生成 ==="
  (cd "$SRC" && MARGIN=$M EBDIR="$RES/eblif_relay" OUTDIR="$CD" SKIP_SPECS=2:0 python3 gen_ext_uniform_all.py $CKTS) | grep -E "config=|生成"
  one() {
    c=$1
    (cd "$SRC" && ATIME=$ATIME python3 place_fixed_tbl.py "$RES/eblif_relay/$c/mapped_$c.v.eblif" "$CD/$c.v") > "$OUT/$c.log" 2>&1
    echo "M=$M $c  $(grep -m1 '^結果:' "$OUT/$c.log" | sed 's/^結果: //' | cut -c1-30)"
  }
  export -f one; export SRC RES ATIME CD OUT M
  echo "=== MARGIN=+$M: 配置配線 (JOBS=$JOBS ATIME=$ATIME) ==="
  echo "$CKTS" | tr ' ' '\n' | xargs -P "$JOBS" -I{} bash -c 'one {}'
  echo "circuit,result,config_m$M,config_m0" > "$OUT/summary.csv"
  for c in $CKTS; do
    r=$(grep -m1 '^結果:' "$OUT/$c.log" | sed 's/^結果: //' | cut -d' ' -f1)
    cm=$(head -1 "$CD/$c.v" | grep -o 'CONFIG=[0-9]*' | cut -d= -f2); c0=$(head -1 "$RES/cone_noskip/$c.v" 2>/dev/null | grep -o 'CONFIG=[0-9]*' | cut -d= -f2)
    echo "$c,$r,$cm,$c0" >> "$OUT/summary.csv"
  done
  echo "=== MARGIN=+$M 集計 ==="; tail -n +2 "$OUT/summary.csv" | cut -d, -f2 | sort | uniq -c
done
