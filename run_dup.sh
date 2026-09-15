#!/bin/bash
# run_dup.sh — fanout 複製版の専用構造に回路を載せる（2026-09-15）
#   手順  ① 中継入り eblif（results/eblif_relay/<回路>/）の fanout > MAXF のセルを複製 → results/eblif_dup/<回路>/
#         ② その eblif から専用構造（skip 0本）を生成 → results/cone_dup/<回路>.v
#         ③ 段固定 CP-SAT（表制約版）で配置配線 → results/place_dup/<回路>.log, summary.csv
#   前提: results/eblif_relay/ があること（無ければ STEP=1 ./run_noskip_superset.sh）
#   使い方: JOBS=4 ATIME=14400 MAXF=2 ./run_dup.sh cat checker9 indep   （回路名を省略すると INFEASIBLE だった14回路）
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); SRC=$ROOT/src; RES=$ROOT/results
JOBS=${JOBS:-4}; ATIME=${ATIME:-3600}; MAXF=${MAXF:-2}
CKTS="${*:-cat checker9 indep lift lift2 lightnew pilot dmac threediff e7 e16 e2 lcu robotben}"
[ -d "$RES/eblif_relay" ] || { echo "results/eblif_relay が無い。先に: STEP=1 ./run_noskip_superset.sh"; exit 1; }
OUT=$RES/place_dup_f$MAXF; mkdir -p "$OUT"
echo "=== fanout ≤ $MAXF に複製 → 専用構造 → 配置配線 (JOBS=$JOBS ATIME=$ATIME) ==="
for c in $CKTS; do
  echo "--- $c"; (cd "$SRC" && MAXF=$MAXF python3 dup_fanout.py "$RES/eblif_relay/$c/mapped_$c.v.eblif" "$RES/eblif_dup_f$MAXF/$c/mapped_$c.v.eblif") | sed 's/^/    /'
done
(cd "$SRC" && EBDIR="$RES/eblif_dup_f$MAXF" OUTDIR="$RES/cone_dup_f$MAXF" SKIP_SPECS=2:0 python3 gen_ext_uniform_all.py $CKTS) | grep -E "config=|生成"
one() {
  c=$1
  (cd "$SRC" && ATIME=$ATIME python3 place_fixed_tbl.py "$RES/eblif_dup_f$MAXF/$c/mapped_$c.v.eblif" "$RES/cone_dup_f$MAXF/$c.v") > "$OUT/$c.log" 2>&1
  echo "$c  $(grep -m1 '^結果:' "$OUT/$c.log" | sed 's/^結果: //' | cut -c1-40)"
}
export -f one; export SRC RES ATIME MAXF OUT
echo "$CKTS" | tr ' ' '\n' | xargs -P "$JOBS" -I{} bash -c 'one {}'
echo "circuit,result" > "$OUT/summary.csv"
for c in $CKTS; do echo "$c,$(grep -m1 '^結果:' "$OUT/$c.log" | sed 's/^結果: //' | cut -d' ' -f1)" >> "$OUT/summary.csv"; done
echo "=== 集計 ($OUT/summary.csv) ==="; tail -n +2 "$OUT/summary.csv" | cut -d, -f2 | sort | uniq -c
