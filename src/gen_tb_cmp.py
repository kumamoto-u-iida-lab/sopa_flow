#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_tb_cmp.py — FatTree（BSGen/src/lib/maketb.py の tb_cmp）と同じ条件で、
   配置配線後の SoPA（Impl＋bitstream）と参照 RTL を同じ入力で動かし、毎クロック出力を比べる tb を作る。2026-10-17。

■ 条件（FatTree と同じ）
  参照 RTL   : rtl_B/<回路>.v（Verilog_B。module top、posedge clk、active-low rst。状態番号は元のまま）
  クロック   : 周期 10ns（always #5 clk = ~clk）
  初期リセット: active-low、3クロック保持し、立下りで解除
  入力の変更 : クロック立下り   / 出力の比較: 立上りの 1ns 後
  途中リセット: ループ番号 128 で 1サイクル（両側に同じ rst）
  入力ベクタ : PI 数（clk/rst を含む .inputs の数）が 12 以下なら全ビット組合せ、
               13 以上なら random.Random(99) の乱数 1,024 本。データ PI k は vec[.inputs 内の位置]
  判定       : if (impl_po !== ref_po) er = er + 1;  不一致 0 回で PASS（片側だけ X/Z も不一致）
  リセット解除前に vec が未初期化になる問題（FatTree の生成 tb）を避けるため、最初に vec = 0 とする。
■ SoPA 側
  Impl は gen_config_verilog.py を CFGPORT=1 で作ったもの（設定値は CONFIG_DATA ポートへ直接。
  シリアル書き込みと実タイミングは対象外＝FatTree と同じ）。
  Impl は元の RTL（negedge clk / active-high rst）の極性で作ってあり、内部で CLK<=~clk, PAE_RST_N<=~rst。
  tb から .clk(~clk), .rst(~rst) で渡すので、ファブリックの FF には tb の clk / rst がそのまま届く
  （FatTree の fabric RESETL = rst と同じ形）。
 使い方: python3 gen_tb_cmp.py <IMPL_V> <EBLIF> [OUTDIR]
   出力: OUTDIR/tb_cmp_<回路>.v, <回路>_vectors.hex（Impl と同じ場所の <回路>.bit を読む）
 環境: RTLB_DIR（既定 <sopa_flow>/rtl_B）
"""
import sys, os, re, random

SD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SD)
RTLB_DIR = os.environ.get("RTLB_DIR", os.path.join(ROOT, "rtl_B"))
MIDRST = 128


def impl_ports(path):
    txt = open(path).read()
    m = re.search(r'module\s+(\w+)_impl\s*\((.*?)\);', txt, re.S)
    ckt, body = m.group(1), m.group(2)
    outs, nbit = [], None
    for p in [s.strip() for s in body.split(',')]:
        mo = re.match(r'(input|output)\s+wire\s*(?:\[(\d+):(\d+)\])?\s*(\w+)$', p)
        if not mo: continue
        kind, hi, _lo, name = mo.groups()
        if name == 'CONFIG_DATA': nbit = int(hi) + 1
        elif kind == 'output': outs.append((name, int(hi) if hi else None))
    if nbit is None:
        sys.exit(f"CONFIG_DATA が外部ポートでない。gen_config_verilog.py を CFGPORT=1 で作り直す: {path}")
    return ckt, outs, nbit


def main():
    implv, eb = sys.argv[1], sys.argv[2]
    od = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(implv))
    ckt, outs, nbit = impl_ports(implv)
    pi = next(l for l in open(eb) if l.startswith('.inputs')).split()[1:]   # clk/rst を含む（FatTree と同じ数え方）
    data_pi = [p for p in pi if p not in ('clk', 'rst')]
    refv = os.path.join(RTLB_DIR, f"{ckt}.v")
    if not os.path.isfile(refv): sys.exit(f"参照 RTL が無い: {refv}")
    ref_ports = re.search(r'module\s+top\s*\((.*?)\);', open(refv).read(), re.S).group(1)
    ref_ports = [s.strip() for s in ref_ports.split(',')]

    npi = len(pi)
    if npi <= 12:
        vecs = list(range(2 ** npi))
    else:                                    # FatTree と同じ乱数列（1つの Random(99) から 1,024 回）
        rng = random.Random(99); vecs = [rng.randrange(2 ** npi) for _ in range(1024)]
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, f"{ckt}_vectors.hex"), "w") as fp:
        for v in vecs: fp.write(f"{v:0{(npi + 3) // 4}x}\n")
    nv = len(vecs)

    owidth = lambda w: (w + 1) if w is not None else 1
    npo = sum(owidth(w) for _, w in outs)
    decl = lambda pre: [f"    wire {f'[{w}:0] ' if w is not None else ''}{pre}_{n};" for n, w in outs]
    cat = lambda pre: "{" + ", ".join(f"{pre}_{n}" for n, _ in reversed(outs)) + "}"
    vw = max(npi - 1, 0)
    ref_conn = []
    for p in ref_ports:
        if p in ('clk', 'rst'): ref_conn.append(f".{p}({p})")
        elif p in data_pi: ref_conn.append(f".{p}(vec[{pi.index(p)}])")
        elif any(p == n for n, _ in outs): ref_conn.append(f".{p}(ref_{p})")
        else: sys.exit(f"参照 RTL のポート {p} の繋ぎ先が分からない")
    impl_conn = [".clk(~clk)", ".rst(~rst)"] + [f".{p}(vec[{pi.index(p)}])" for p in data_pi] \
        + [f".{n}(impl_{n})" for n, _ in outs] + [".CONFIG_DATA(cfg)"]

    L = ["`timescale 1ns/1ps",
         f"// {ckt}: SoPA（{os.path.basename(implv)} ＋ {ckt}.bit）vs 参照 RTL（rtl_B、module top）。FatTree の tb_cmp と同じ条件",
         f"module tb_cmp_{ckt};",
         "    reg clk = 1'b0;", "    always #5 clk = ~clk;", "    reg rst;",
         f"    localparam NV = {nv};", f"    localparam NCYC = {nv};", f"    localparam MIDRST = {MIDRST};",
         f"    localparam NBIT = {nbit};",
         f"    reg  [{vw}:0] vec;", f"    reg  [{max(npi - 1, 3)}:0] vmem [0:NV-1];",
         "    reg  [NBIT-1:0] cmem [0:0];", "    reg  [NBIT-1:0] cfg;"] \
        + decl("ref") + decl("impl") + [
         f"    wire [{npo - 1}:0] ref_po  = {cat('ref')};",
         f"    wire [{npo - 1}:0] impl_po = {cat('impl')};",
         "    top u_ref (" + ", ".join(ref_conn) + ");",
         f"    {ckt}_impl u_impl (" + ", ".join(impl_conn) + ");",
         "    integer v, er;",
         "    initial begin",
         "        er = 0; vec = 0;                       // リセット解除前の入力を 0 に（未初期化 X を避ける）",
         f'        $readmemb("{ckt}.bit", cmem); cfg = cmem[0];',
         '        if (^cfg === 1\'bx) begin $display("FATAL: bitstream の読み込みに失敗"); $finish; end',
         f'        $readmemh("{ckt}_vectors.hex", vmem);',
         "        rst = 1'b0;                            // active-low assert",
         "        repeat (3) @(posedge clk);",
         "        @(negedge clk); rst = 1'b1;            // release",
         "        for (v = 0; v < NCYC; v = v + 1) begin",
         "            @(negedge clk);",
         "            rst = (v == MIDRST) ? 1'b0 : 1'b1;   // 途中リセット",
         f"            vec = vmem[(v % NV)][{vw}:0];",
         "            @(posedge clk); #1;",
         "            if (impl_po !== ref_po) begin",
         "                er = er + 1;",
         '                if (er <= 5) $display("  MISMATCH v=%0d vec=%h ref=%b impl=%b", v, vec, ref_po, impl_po);',
         "            end",
         "        end",
         f'        if (er == 0) $display("PASS: {ckt} (seq, %0d cyc)", NCYC);',
         f'        else         $display("FAIL: {ckt}  元RTL {{%0d}} / %0d cyc", er, NCYC);',
         "        $finish;", "    end", "endmodule"]
    out = os.path.join(od, f"tb_cmp_{ckt}.v")
    open(out, "w").write("\n".join(L) + "\n")
    print(f"{ckt}: PI {npi}（データ {len(data_pi)}）→ ベクタ {nv} 本（{'全組合せ' if npi <= 12 else '乱数 seed 99'}）  出力 {npo}bit  CONFIG {nbit}bit")
    print(f"  {out}")


if __name__ == '__main__':
    main()
