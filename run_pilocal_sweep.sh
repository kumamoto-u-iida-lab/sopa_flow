#!/bin/bash
# run_pilocal_sweep.sh — pilocal（PI ノードを論理の1つ上、ia に専用 EXT 1本）を PA 数 1,152/1,536/1,920/2,304/3,072 で作った5構造に
#   small 41回路を配置する。2026-10-22。FatTree の CLB 内 PAE 数 6/8/10/12/16（64 CLB、×3 で PA 数）と収容能力をそろえる比較。
#   構造: structures/superset_pilocal_pa<N>_alt_cyc.v（ネットリスト 19段 ＋ 1段、足した行は下の行と同じ列数）
#   選び方ごとに run_ext_nest.sh（段固定 → 載らなければ案B・子ごと）。PA 数どうしも PAR 本並列。
# 使い方:  bash run_pilocal_sweep.sh > pilocal_sweep.log 2>&1 &
# 環境:    SIZES（既定 "1536 1152 1920 2304 3072"）PAR（既定 2）JOBS（既定 2）ATIME1（600）ATIME2（3600）THREADS（8）
# 出力:    results/pilocal_sweep/pa<N>/summary.txt
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); cd "$ROOT"
SIZES=${SIZES:-"1536 1152 1920 2304 3072"}
PAR=${PAR:-2}; export JOBS=${JOBS:-2} ATIME1=${ATIME1:-600} ATIME2=${ATIME2:-3600} THREADS=${THREADS:-8}
export EBR=data/eblif_pilocal CAND_RULE=alt_cyc
one_size() {
  n=$1; st=structures/superset_pilocal_pa${n}_alt_cyc.v
  echo "[$(date +%m/%d\ %H:%M)] 開始 pa$n"
  SUPERSET=$st OUT=results/pilocal_sweep/pa$n bash run_ext_nest.sh > results/pilocal_sweep/pa$n.log 2>&1
  echo "[$(date +%m/%d\ %H:%M)] 終了 pa$n  $(tail -1 results/pilocal_sweep/pa$n/summary.txt 2>/dev/null)"
}
export -f one_size; export ROOT
mkdir -p results/pilocal_sweep
echo $SIZES | tr ' ' '\n' | xargs -P "$PAR" -I{} bash -c 'one_size {}'
for n in $SIZES; do echo "pa$n: $(tail -1 results/pilocal_sweep/pa$n/summary.txt 2>/dev/null)"; done
