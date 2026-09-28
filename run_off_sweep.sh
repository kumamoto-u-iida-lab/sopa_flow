#!/bin/bash
# run_off_sweep.sh — 段固定＋OFFSET（place_fixed_off.py）で、回路ごとに OFFSET=0,1,2 を順に試し、最初に載った OFFSET を記録（2026-09-28）
#   FF を下3行に置いた構造（NFFSTAGES=3）を使うこと。FF の無い段へのずらしはツールが「INFEASIBLE(FF無し)」で弾く。
#   使い方: RULE=cyclic_eq SUPERSET=structures/superset_allrelay_s125_ff3_cyclic_eq.v OUT=results/offsweep_cyc \
#           JOBS=4 ATIME=3600 ./run_off_sweep.sh <回路名...>
#   環境: EBR（中継入り eblif の親dir, 既定 results/eblif_relay） OFFSETS（既定 "0 1 2"）
set -u
ROOT=$(cd "$(dirname "$0")" && pwd)
RULE=${RULE:?RULE を指定}; SUPERSET=${SUPERSET:?SUPERSET を指定}; OUT=${OUT:?OUT を指定}
EBR=${EBR:-$ROOT/results/eblif_relay}; OFFSETS=${OFFSETS:-"0 1 2"}; JOBS=${JOBS:-4}; ATIME=${ATIME:-3600}
[ "${SUPERSET#/}" = "$SUPERSET" ] && SUPERSET=$ROOT/$SUPERSET
[ "${EBR#/}" = "$EBR" ] && EBR=$ROOT/$EBR
[ "${OUT#/}" = "$OUT" ] && OUT=$ROOT/$OUT
mkdir -p "$OUT"
echo "=== OFFSET スイープ RULE=$RULE OFFSETS=[$OFFSETS] JOBS=$JOBS ATIME=$ATIME 構造=$(basename $SUPERSET) ==="
one() {
  c=$1; res=""; hist=""
  for off in $OFFSETS; do
    log="$OUT/${c}_off$off.log"
    (cd "$ROOT/src" && CAND_RULE=$RULE OFFSET=$off ATIME=$ATIME python3 place_fixed_off.py "$EBR/$c/mapped_$c.v.eblif" "$SUPERSET") > "$log" 2>&1
    rm -f "$ROOT/src/place_fixed_off_$c.json"
    r=$(grep -m1 '^結果:' "$log" | sed 's/^結果: //' | awk '{print $1, $2}')
    hist="$hist off$off=$r"
    case "$r" in OPTIMAL*|FEASIBLE*) res="OPTIMAL@off$off"; break;; esac
  done
  [ -z "$res" ] && res="NG"
  echo "$c $res |$hist"
}
export -f one; export ROOT RULE SUPERSET OUT EBR OFFSETS ATIME
printf '%s\n' "$@" | xargs -P "$JOBS" -I{} bash -c 'one {}' | tee "$OUT/summary.txt"
echo "=== 集計: 載った $(grep -c OPTIMAL@ "$OUT/summary.txt") / $(wc -l < "$OUT/summary.txt") 回路 ==="
