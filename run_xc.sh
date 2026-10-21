#!/bin/bash
# run_xc.sh — r1536 を土台に「EXT 45本を受ける列を行ごとに絞った」4構造（列の選び方 head/tail/even/reach2）に small 41回路を配置する。2026-10-21。
#   構造: structures/superset_r1536_xc_<選び方>_alt_cyc.v（EXT の列 = ② の行ごとの「PI を読むセルの最大」×1.2 切り上げ、計195列、ia・ib 両方に45本）
#   ネットリスト: ② results/eblif_relay（PI ノード無し、論理セルが PI を直接読む）
#   選び方ごとに run_ext_nest.sh（段固定 → 載らなければ案B・子ごと）。選び方どうしも PAR 本並列。
# 使い方:  bash run_xc.sh > xc_run.log 2>&1 &
# 環境:    SELS（既定 "even reach2 tail head"）PAR（既定 2）JOBS（既定 2）ATIME1（600）ATIME2（3600）THREADS（8）
# 出力:    results/xc/<選び方>/summary.txt
set -u
ROOT=$(cd "$(dirname "$0")" && pwd); cd "$ROOT"
SELS=${SELS:-"even reach2 tail head"}
PAR=${PAR:-2}; export JOBS=${JOBS:-2} ATIME1=${ATIME1:-600} ATIME2=${ATIME2:-3600} THREADS=${THREADS:-8}
export EBR=results/eblif_relay CAND_RULE=alt_cyc
one_sel() {
  s=$1; st=structures/superset_r1536_xc_${s}_alt_cyc.v
  echo "[$(date +%m/%d\ %H:%M)] 開始 $s"
  SUPERSET=$st OUT=results/xc/$s bash run_ext_nest.sh > results/xc/$s.log 2>&1
  echo "[$(date +%m/%d\ %H:%M)] 終了 $s  $(tail -1 results/xc/$s/summary.txt 2>/dev/null)"
}
export -f one_sel; export ROOT
mkdir -p results/xc
# ② 中継入りネットリスト（git 管理外）が無ければ data/eblif_from_rtl から作る（手元の 41本と cmp で一致を確認済み）
[ "$(ls results/eblif_relay 2>/dev/null | wc -l)" -ge 41 ] || python3 src/insert_relay.py > results/xc/insert_relay.log 2>&1
echo $SELS | tr ' ' '\n' | xargs -P "$PAR" -I{} bash -c 'one_sel {}'
for s in $SELS; do echo "$s: $(tail -1 results/xc/$s/summary.txt 2>/dev/null)"; done
