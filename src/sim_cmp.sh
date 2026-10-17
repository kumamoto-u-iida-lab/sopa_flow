#!/bin/bash
# sim_cmp.sh — 配置結果から Impl（cfg ポート版）と bitstream を作り、FatTree と同じ条件の tb_cmp で
#   参照 RTL（rtl_B）と毎クロック比較する（iverilog）。2026-10-17。条件は src/gen_tb_cmp.py の先頭。
# 使い方: bash src/sim_cmp.sh <回路> <構造.v> <配置json> [出力dir]
#   例) CAND_RULE=alt_cyc bash src/sim_cmp.sh girl10 structures/superset_r1536pi_ff7_alt_cyc.v results/equiv_ff7/place_fixed_tbl_girl10.json
# 環境: EBR（eblif の親dir, 既定 data/eblif_pinode） CAND_RULE（構造を作ったときと同じ値, 既定 alt_cyc）
set -u
SD=$(cd "$(dirname "$0")" && pwd); ROOT=$(dirname "$SD")
CKT=$1; CONE=$(realpath "$2"); PJ=$(realpath "$3")
OUT=${4:-$ROOT/results/sim_cmp/$CKT}; mkdir -p "$OUT"; OUT=$(realpath "$OUT")
EBR=${EBR:-$ROOT/data/eblif_pinode}; EB=$(realpath "$EBR/$CKT/mapped_$CKT.v.eblif")
export CAND_RULE=${CAND_RULE:-alt_cyc}
cd "$OUT" || exit 2
CFGPORT=1 python3 "$SD/gen_config_verilog.py" "$EB" "$CONE" "$PJ" "impl_$CKT.v" | grep -E '警告|CONFIG' || exit 2
python3 "$SD/gen_tb_cmp.py" "impl_$CKT.v" "$EB" . | head -1
iverilog -g2012 -o "tb_cmp_$CKT" "tb_cmp_$CKT.v" "impl_$CKT.v" "$CONE" "$ROOT/rtl_B/$CKT.v" || exit 2
vvp -n "tb_cmp_$CKT" | grep -E 'PASS|FAIL|MISMATCH|FATAL'
