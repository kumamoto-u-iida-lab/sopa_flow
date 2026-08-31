#!/bin/bash
# equiv_check.sh — Ref(元RTL) と Impl(SoPA+config焼き込み) の等価性を yosys の SAT で検査する。
#   VCS/iverilog 無しでローカル実行できる。リセットを1段目に与え、以降の全入力組合せを網羅して
#   出力が食い違う入力列が存在しないことを SAT で示す(有限段の証明)。
#
#   使い方: ./equiv_check.sh <回路名> [段数(既定16)]
#     事前に impl_<回路>.v (CFGPORT無し=CONFIG焼き込み版) が results/ にあること。
#
#   ※対照実験(2026-08-06, girl10): .CLK / .PAE_RST_N の極性をわざと壊すと3通りとも FAIL になる
#     ことを確認済み。この検査はクロック極性・リセット極性の誤りを検出できる。
set -u
CKT=${1:?回路名を指定}
N=${2:-16}
SD=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$SD")
# ★2026-08-31: sopa_flow の構成に合わせ、yosys は PATH から探す（絶対パス直書きをやめた）。
#   どれも環境変数で上書きできる: YOSYS / RTL_DIR / CONE / IMPL
YOSYS=${YOSYS:-$(command -v yosys)}
[ -n "${YOSYS:-}" ] || { echo "yosys が PATH にない。環境変数 YOSYS でパスを指定してください。"; exit 2; }
RTL_DIR=${RTL_DIR:-$ROOT/rtl}
REF=$RTL_DIR/$CKT.v
CONE=${CONE:-$ROOT/results/cone_ext_uniform/$CKT.v}
IMPL=${IMPL:-$ROOT/results/impl_$CKT.v}

for f in "$REF" "$CONE" "$IMPL"; do
  [ -f "$f" ] || { echo "$CKT: 見つからない -> $f"; exit 2; }
done

SETS="-set-at 1 in_rst 1"
for k in $(seq 2 "$N"); do SETS="$SETS -set-at $k in_rst 0"; done

# Refのモジュール名はファイル名と一致しないことがある (ass13_no_decoder.v の中身は module ass13)
REFMOD=$(grep -m1 -oP '\bmodule\s+\K\w+' "$REF")

OUT=$("$YOSYS" -p "
read_verilog $REF
read_verilog $CONE $IMPL
hierarchy -check; proc; opt; memory; opt
miter -equiv -flatten $REFMOD ${CKT}_impl miter
hierarchy -top miter; async2sync; opt
sat -verify -prove trigger 0 -seq $N -set-init-undef -set-def-inputs $SETS miter" 2>&1)

if grep -q "SAT proof finished - no model found: SUCCESS" <<<"$OUT"; then
  echo "$CKT: EQUIVALENT  (${N}段, 全入力組合せ網羅)"
  exit 0
else
  echo "$CKT: NOT-EQUIVALENT または検査失敗 (${N}段)"
  grep -E "ERROR|proof did fail" <<<"$OUT" | head -3
  exit 1
fi
