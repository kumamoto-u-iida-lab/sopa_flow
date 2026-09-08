#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_conf_chain.py — SoPA 構造 .v に【構成メモリ（CONF_FF のスキャンチェーン）】を付けた面積測定用トップを作る。

2026-09-08 作成。先生 9/4 の指摘「島は構成メモリ込み、SoPA/IPGen は抜き。揃えろ」への対応。
先輩の例（rtl/CONF_FF.v, CONF_FF_TILE_3096.v, FPGA_CORE.v）と同じ作り:
  CONF_FF        1bit のシフトレジスタ。CONF_MODE=1 で CONF_IN を取り込み、CF = CONF_E & Tmp を出す。非同期 CONF_RESETL
  CONF_FF_TILE_N CONF_FF を N 個直列（CONF_IN → CF0 → CF1 … → CONF_OUT）。CF[N-1:0] が構成メモリの値
  FPGA_CORE      CONF_FF_TILE_N の CF を ファブリックの CONFIG_DATA へ渡すトップ
ここでは SoPA 用に SOPA_CORE を作る（ポート: CLK, PAE_RST_N, I, EXT, pa_o, CONF_CLK, CONF_RESETL, CONF_MODE, CONF_IN, CONF_E, CONF_OUT）。

 使い方: python3 gen_conf_chain.py <構造.v> <出力.v>
   出力 = 構造 .v の全文 ＋ CONF_FF ＋ CONF_FF_TILE_N ＋ SOPA_CORE。DC は top=SOPA_CORE で合成する。
"""
import sys, re
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()
m = re.search(r'input\s+wire\s+\[(\d+):0\]\s+CONFIG_DATA', t)
N = int(m.group(1)) + 1
# ファブリックのトップ = ポートリストに CONFIG_DATA を持つ module
mod = [mm.group(1) for mm in re.finditer(r'^module\s+(\w+)\s*\((.*?)\);', t, re.M | re.S) if 'CONFIG_DATA' in mm.group(2)][-1]
ports = {}
for name in ("I", "EXT", "pa_o"):
    mm = re.search(r'(input|output)\s+wire\s+\[(\d+):0\]\s+' + name + r'\b', t)
    if mm: ports[name] = int(mm.group(2)) + 1
L = []
L.append(f"\n// ===== 構成メモリ（先輩の CONF_FF / CONF_FF_TILE と同じ作り）: {N} bit =====")
L.append("""module CONF_FF(CONF_OUT, CF, CONF_RESETL, CONF_MODE, CONF_IN, CONF_E, CONF_CLK);
   input CONF_RESETL; input CONF_MODE; input CONF_IN; input CONF_E; input CONF_CLK;
   output CONF_OUT; output CF;
   reg Tmp;
   always @(posedge CONF_CLK or negedge CONF_RESETL)
     if (~CONF_RESETL) Tmp <= 1'b0;
     else if (CONF_MODE) Tmp <= CONF_IN;
     else Tmp <= Tmp;
   assign CF = (CONF_E & Tmp);
   assign CONF_OUT = Tmp;
endmodule""")
L.append(f"module CONF_FF_TILE_{N}(CONF_OUT, CF, CONF_RESETL, CONF_MODE, CONF_IN, CONF_E, CONF_CLK);")
L.append("  input CONF_RESETL; input CONF_MODE; input CONF_IN; input CONF_E; input CONF_CLK;")
L.append(f"  output CONF_OUT; output [{N-1}:0] CF;")
L.append(f"  wire [{N-2}:0] CONF_TMP_CF;")
for i in range(N):
    cin = "CONF_IN" if i == 0 else f"CONF_TMP_CF[{i-1}]"
    cout = "CONF_OUT" if i == N - 1 else f"CONF_TMP_CF[{i}]"
    L.append(f"  CONF_FF CF{i}(.CONF_RESETL(CONF_RESETL), .CONF_MODE(CONF_MODE), .CONF_IN({cin}), .CONF_E(CONF_E), .CONF_CLK(CONF_CLK), .CONF_OUT({cout}), .CF(CF[{i}]));")
L.append("endmodule")
pl = ["  input wire CLK", "  input wire PAE_RST_N"]
if "I" in ports: pl.append(f"  input wire [{ports['I']-1}:0] I")
if "EXT" in ports: pl.append(f"  input wire [{ports['EXT']-1}:0] EXT")
pl.append(f"  output wire [{ports['pa_o']-1}:0] pa_o")
pl += ["  input wire CONF_CLK", "  input wire CONF_RESETL", "  input wire CONF_MODE", "  input wire CONF_IN", "  input wire CONF_E", "  output wire CONF_OUT"]
L.append("module SOPA_CORE (\n" + ",\n".join(pl) + "\n);")
L.append(f"  wire [{N-1}:0] CONFIG_DATA;")
L.append(f"  CONF_FF_TILE_{N} CONF_TILE(.CONF_RESETL(CONF_RESETL), .CONF_MODE(CONF_MODE), .CONF_IN(CONF_IN), .CONF_E(CONF_E), .CONF_CLK(CONF_CLK), .CONF_OUT(CONF_OUT), .CF(CONFIG_DATA));")
conn = [".CLK(CLK)", ".PAE_RST_N(PAE_RST_N)"]
if "I" in ports: conn.append(".I(I)")
if "EXT" in ports: conn.append(".EXT(EXT)")
conn += [".pa_o(pa_o)", ".CONFIG_DATA(CONFIG_DATA)"]
L.append(f"  {mod} FABRIC(" + ", ".join(conn) + ");")
L.append("endmodule")
open(out, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + "\n".join(L) + "\n")
print(f"{src} → {out}: 構成メモリ {N} bit のチェーン + SOPA_CORE（ファブリック module={mod}, ports={ports}）")
