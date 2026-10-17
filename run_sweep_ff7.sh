#!/bin/bash
# run_sweep_ff7.sh — ff7 の作り方のまま大きさを振った構造（包絡線 1,216PA × 倍率）に small 41回路を配置する。2026-10-17。
#   倍率ごとに run_ext_nest.sh（段固定 → 載らなければ案B・子ごと）を回す。倍率どうしも並列に走らせる。
#   構造: structures/superset_pi_ff7_s<倍率>_alt_cyc.v（s100=1.00倍 … s150=1.50倍）。1.263倍は ff7 そのもの
#         （structures/superset_r1536pi_ff7_alt_cyc.v、既に results/place_r1536pi_ff7 で回したなら SCALES から外す）。
#   列数の規則: 行0(FF)=7・最上段=45 固定、他の行は ⌈包絡線×倍率⌉、入力側の行 ≤ 2×FF 側の隣の行。
# 使い方:  bash run_sweep_ff7.sh > sweep_ff7.log 2>&1 &
# 環境:    SCALES（既定 "100 105 110 115 120 135 150"、"1263" で ff7）  PAR（同時に走らせる倍率の数, 既定 2）
#          JOBS（1つの倍率の中で同時に回す回路数, 既定 2）  ATIME1（段固定, 既定 600）  ATIME2（案B, 既定 3600）  THREADS（既定 8）
# メモリ:  案B は 1本 5〜16GB。同時に走るのは最大 PAR×JOBS 本。空きメモリ(GB) ÷ 12 くらいを PAR×JOBS に
# 出力:    results/sweep_ff7/s<倍率>/（run_ext_nest.sh と同じ: <回路>_fixed.log / _B.log / summary.txt）
#          最後に python3 src/collect_sweep_ff7.py で results/sweep_ff7/sweep_ff7.csv（回路×倍率の表）
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); cd "$ROOT"
SCALES=${SCALES:-"100 105 110 115 120 135 150"}
PAR=${PAR:-2}; export JOBS=${JOBS:-2} ATIME1=${ATIME1:-600} ATIME2=${ATIME2:-3600} THREADS=${THREADS:-8}
export EBR=data/eblif_pinode CAND_RULE=alt_cyc
one_scale() {
  s=$1
  if [ "$s" = 1263 ]; then st=structures/superset_r1536pi_ff7_alt_cyc.v; else st=structures/superset_pi_ff7_s${s}_alt_cyc.v; fi
  [ -f "$st" ] || { echo "構造が無い: $st"; return; }
  echo "[$(date +%m/%d\ %H:%M)] 開始 s$s  $st"
  SUPERSET=$st OUT=results/sweep_ff7/s$s bash run_ext_nest.sh > results/sweep_ff7/s$s.log 2>&1
  echo "[$(date +%m/%d\ %H:%M)] 終了 s$s  $(tail -1 results/sweep_ff7/s$s/summary.txt 2>/dev/null)"
}
export -f one_scale; export ROOT
mkdir -p results/sweep_ff7
echo "倍率=$SCALES  PAR=$PAR JOBS=$JOBS  段固定 ${ATIME1}s → 案B ${ATIME2}s"
echo $SCALES | tr ' ' '\n' | xargs -P "$PAR" -I{} bash -c 'one_scale {}'
python3 src/collect_sweep_ff7.py
