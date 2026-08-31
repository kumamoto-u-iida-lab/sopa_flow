#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_cone_ext.py — gen_cone_spindle.py の複製＋段ごと外部入力(N_EXT[c])対応版。
   元の gen_cone_spindle.py は変更しない。差分は「N_EXT を段ごとのリストにできる」点のみ。
   段cのIMUXに next_ext[c] 本の外部入力(EXTバス)を選択肢として加える。config が段別に変わる。

   使い方: python3 gen_cone_ext.py <FF側->入力側の幅リスト>
   環境変数:
     NEXT   … 段別外部入力数(入力側->FF側の順, カンマ区切り, 長さD)。既定=全0。
              例) NEXT=7,7,5,4,3,2,1,0,0,0
     NEXTTAG… 出力ファイル名の接尾辞(uni/tap等)。既定=""。
   出力: cone_spindle_<a-b-...>[_<NEXTTAG>].v / .png"""
import sys, math, os
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAVE_PLT = True
except Exception:
    HAVE_PLT = False


def gen_pattern(n_src, n_dst):
    N = n_dst
    cand = {j: [] for j in range(n_dst)}
    cur = 0
    for k in range(1, n_src + 1):
        a = min(N, (2 * N) // k)
        for _ in range(a):
            cand[cur % n_dst].append(k - 1)
            cur += 1
    return [sorted(set(cand[j])) for j in range(n_dst)]


# ---- 引数: FF側->入力側 の幅リスト ----
if len(sys.argv) > 1 and "," in sys.argv[1]:
    ff_to_in = [int(x) for x in sys.argv[1].split(",")]
else:
    ff_to_in = [3, 6, 12, 24, 12]

widths = list(reversed(ff_to_in))        # widths[0]=入力側 ... [D-1]=FF側
D = len(widths)
B = widths[-1]

# ---- 段別 外部入力数 next_ext[c] (入力側->FF側) ----
if os.environ.get("NEXT"):
    next_ext = [int(x) for x in os.environ["NEXT"].split(",")]
    assert len(next_ext) == D, f"NEXT長さ{len(next_ext)} != D{D}"
else:
    next_ext = [0] * D
NEXT_MAX = max(next_ext) if next_ext else 0
NEXTTAG = os.environ.get("NEXTTAG", "")

TAG = "spindle_" + "-".join(map(str, ff_to_in)) + (("_" + NEXTTAG) if NEXTTAG else "")
SD = os.path.dirname(os.path.abspath(__file__))

patterns = []
for s in range(D - 1):
    patterns.append(gen_pattern(widths[s], widths[s + 1]))

print(f"幅(入力側->FF側) = {widths}   段数D={D}  FF={B}個")
print(f"段別外部入力 next_ext(入力->FF) = {next_ext}  (EXTバス幅={NEXT_MAX})")

SELW = lambda n: max(1, math.ceil(math.log2(n)))
# skip の行選択に要るビット数。出発段の幅が1なら選ぶ相手が1本しかない＝muxも設定ビットも不要(0bit)。
SKW = lambda n: 0 if n <= 1 else SELW(n)
SKIP_SPECS = [(2, 4), (3, 2), (4, 1)]
if os.environ.get("SKIP_SPECS"):
    SKIP_SPECS = [(int(a), int(b)) for a, b in
                  (t.split(":") for t in os.environ["SKIP_SPECS"].split(",")) if int(b) > 0]

# 段別 skip枠 SKIPMAP="c,d,cnt;c,d,cnt;..." (行き先段c, 距離d, 本数cnt)。指定時は固定SKIP_SPECSを上書き。
SKIPMAP = {}
if os.environ.get("SKIPMAP"):
    for t in os.environ["SKIPMAP"].split(";"):
        if not t.strip():
            continue
        c, d, cnt = (int(x) for x in t.split(","))
        SKIPMAP[(c, d)] = cnt


def skips_at(c):
    res = []
    if SKIPMAP:                                  # 段別実需要モード
        for d in range(2, D):
            for j in range(SKIPMAP.get((c, d), 0)):
                res.append((d, j))
    else:                                        # 固定 SKIP_SPECS モード
        for dist, cnt in SKIP_SPECS:
            if c - dist >= 0:
                for j in range(cnt):
                    res.append((dist, j))
    return res


owire = lambda c, i: f"o_c{c}_{i}"
skipwire = lambda c, d, j: f"sel_skip_c{c}_d{d}_{j}"

PA_MODULE = """module PA (
    input wire PA_I_A, input wire PA_I_B, output wire PA_O_A, input wire [1:0] PROG_DATA);
    wire w_n0, w_n1;
    assign w_n0 = PA_I_B ^ PROG_DATA[0];
    assign w_n1 = PA_I_A & w_n0;
    assign PA_O_A = w_n1 ^ PROG_DATA[1];
endmodule"""
FF_MODULE = """module FLIPFLOP_NODE (
    input wire CLK, input wire PAE_RST_N, input wire FFNODE_I,
    output reg FFNODE_O, input wire PROG_DATA);
    reg r_o;
    always @(posedge CLK or negedge PAE_RST_N)
        if(~PAE_RST_N) r_o <= 1'b0; else r_o <= FFNODE_I;
    always @(*) FFNODE_O = PROG_DATA ? FFNODE_I : r_o;
endmodule"""


def imux_modules(sizes):
    out = []
    for n in sorted(s for s in sizes if s >= 2):
        w = SELW(n)
        ins = ", ".join(f"input wire IMUX_I_{i}" for i in range(n))
        cs = "\n".join(f"        {w}'d{i}: IMUX_O = IMUX_I_{i};" for i in range(n))
        out.append(f"module IMUX_IN{n:03d} ({ins}, output reg IMUX_O, input wire [{w-1}:0] PROG_DATA);\n"
                   f"    always @(*) case (PROG_DATA[{w-1}:0])\n{cs}\n"
                   f"        default: IMUX_O = 1'bx;\n    endcase\nendmodule")
    return "\n\n".join(out)


def gen_verilog():
    Wmax = widths[0]
    NFF = int(os.environ.get("NFFSTAGES", "1"))          # FF可能な段数(最下段から)。既定1
    FFSTAGES = list(range(max(1, D - NFF), D))            # 例 NFF=3, D=18 -> [15,16,17]
    n_ff = sum(widths[c] for c in FFSTAGES)              # 全FF出力数(=pa_o幅)。全IMUXに専用フィードバックとして入れる
    ff_wires = [f"o_c{c}_{i}" for c in FFSTAGES for i in range(widths[c])]  # 全FF出力(owire)
    pos = 0
    skip_cfg = {}
    for c in range(1, D):
        for (dist, j) in skips_at(c):
            skip_cfg[(c, dist, j)] = (pos, SKW(widths[c - dist]))
            pos += SKW(widths[c - dist])
    n_skip_bits = pos
    imux_cfg = {}
    for c in range(1, D):
        nin = len(skips_at(c))
        for i in range(widths[c]):
            n = len(patterns[c - 1][i]) + nin + n_ff + next_ext[c] + 2
            for port in ('ia', 'ib'):
                imux_cfg[(c, i, port)] = (pos, SELW(n)); pos += SELW(n)
    n_imux_bits = pos - n_skip_bits
    pa_cfg = {}
    for c in range(D):
        for i in range(widths[c]):
            pa_cfg[(c, i)] = pos; pos += 2
    ff_cfg = {}
    for c in FFSTAGES:
        for i in range(widths[c]):
            ff_cfg[(c, i)] = pos; pos += 1
    n_cfg = pos

    sizes = set()
    for c in range(1, D):
        nin = len(skips_at(c))
        for i in range(widths[c]):
            sizes.add(len(patterns[c - 1][i]) + nin + n_ff + next_ext[c] + 2)
        for (dist, j) in skips_at(c):
            sizes.add(widths[c - dist])

    L = []
    L.append(f"// spindle widths(入力側->FF側)={widths}  N_EXT_LIST={next_ext}  EXTBUS={NEXT_MAX}  CONFIG={n_cfg}bit")
    L.append(f"//   skip={n_skip_bits} / imux={n_imux_bits} / pa={sum(widths)*2} / ff={n_ff} (最下段/FF側のみ)")
    L.append(PA_MODULE); L.append(""); L.append(FF_MODULE); L.append("")
    L.append(imux_modules(sizes)); L.append("")

    L.append("module cone (")
    L.append("    input  wire CLK,")
    L.append("    input  wire PAE_RST_N,")
    if Wmax:                                         # width[0]=0(段0が空)ならIポート省略
        L.append(f"    input  wire [{2*Wmax-1}:0] I,")
    if NEXT_MAX:
        L.append(f"    input  wire [{NEXT_MAX-1}:0] EXT,")
    L.append(f"    output wire [{n_ff-1}:0] pa_o,")
    L.append(f"    input  wire [{n_cfg-1}:0] CONFIG_DATA")
    L.append(");")
    ow = [owire(c, i) for c in range(D) for i in range(widths[c])]
    for j in range(0, len(ow), 12):
        L.append("    wire " + ", ".join(ow[j:j+12]) + ";")
    sw = [f"sel_c{c}_{i}_{p}" for c in range(1, D) for i in range(widths[c]) for p in ('ia', 'ib')]
    for j in range(0, len(sw), 12):
        L.append("    wire " + ", ".join(sw[j:j+12]) + ";")
    skw = [skipwire(c, d, j) for c in range(1, D) for (d, j) in skips_at(c)]
    for j in range(0, len(skw), 12):
        if skw[j:j+12]:
            L.append("    wire " + ", ".join(skw[j:j+12]) + ";")
    ffn = [f"ffn_c{c}_{i}" for c in FFSTAGES for i in range(widths[c])]
    for j in range(0, len(ffn), 12):
        L.append("    wire " + ", ".join(ffn[j:j+12]) + ";")
    L.append("")

    L.append(f"    // ===== 段0 (入力側, w={Wmax}) : PA が外部入力 I を直受け =====")
    for i in range(Wmax):
        L.append(f"    PA pa_c0_{i} (.PA_I_A(I[{2*i}]), .PA_I_B(I[{2*i+1}]), "
                 f".PA_O_A({owire(0,i)}), .PROG_DATA(CONFIG_DATA[{pa_cfg[(0,i)]} +: 2]));")
    L.append("")

    for c in range(1, D):
        sk = skips_at(c)
        ne = next_ext[c]
        L.append(f"    // ===== 段{c} (w={widths[c]}) の IMUX (前段{c-1} + skip{[d for d,_ in sk]} + EXT{ne}) =====")
        for (dist, j) in sk:
            st, w = skip_cfg[(c, dist, j)]
            L.append(f"    // skip: 行{c-dist}→行{c} ({dist}段飛び) #{j}")
            if w == 0:      # 出発段の幅が1: 選択の余地が無いので mux を置かず直結(設定ビットも消費しない)
                L.append(f"    assign {skipwire(c,dist,j)} = {owire(c-dist, 0)};"
                         f"  // 行{c-dist}は幅1のため選択不要")
                continue
            conn = ", ".join(f".IMUX_I_{t}({owire(c-dist, t)})" for t in range(widths[c-dist]))
            L.append(f"    IMUX_IN{widths[c-dist]:03d} omux_c{c}_d{dist}_{j} ({conn}, "
                     f".IMUX_O({skipwire(c,dist,j)}), .PROG_DATA(CONFIG_DATA[{st} +: {w}]));")
        skin = [skipwire(c, dist, j) for (dist, j) in sk]
        ffb_in = list(ff_wires)                              # 全FF出力を専用フィードバックとして全IMUXに入れる
        ext_in = [f"EXT[{e}]" for e in range(ne)]            # 段cは先頭ne本をタップ
        const_in = ["1'b0", "1'b1"]
        for i in range(widths[c]):
            ci = patterns[c-1][i]; nbase = len(ci)
            ntot = nbase + len(skin) + n_ff + ne + 2
            L.append(f"    // 行{c} PA{i}: 候補(前行)= {ci}"
                     + (f" + skip{len(skin)}本" if skin else "")
                     + (f" + FFfb{n_ff}本" if n_ff else "")
                     + (f" + EXT{ne}本" if ne else "")
                     + " + 定数2本")
            for port in ('ia', 'ib'):
                ins = [owire(c-1, ci[k]) for k in range(nbase)] + skin + ffb_in + ext_in + const_in
                conn = ", ".join(f".IMUX_I_{k}({ins[k]})" for k in range(ntot))
                st, w = imux_cfg[(c, i, port)]
                L.append(f"    IMUX_IN{ntot:03d} imux_c{c}_{i}_{port} ({conn}, "
                         f".IMUX_O(sel_c{c}_{i}_{port}), .PROG_DATA(CONFIG_DATA[{st} +: {w}]));")
        for i in range(widths[c]):
            o = f"ffn_c{c}_{i}" if c in FFSTAGES else owire(c, i)
            L.append(f"    PA pa_c{c}_{i} (.PA_I_A(sel_c{c}_{i}_ia), .PA_I_B(sel_c{c}_{i}_ib), "
                     f".PA_O_A({o}), .PROG_DATA(CONFIG_DATA[{pa_cfg[(c,i)]} +: 2]));")
        L.append("")

    L.append(f"    // ===== 最下段(FF側, 段{D-1}, 幅{B}) の全PA出力に FLIPFLOP_NODE ({n_ff}個) =====")
    k = 0
    for c in FFSTAGES:
        for i in range(widths[c]):
            st = ff_cfg[(c, i)]
            L.append(f"    FLIPFLOP_NODE ff_c{c}_{i} (.CLK(CLK), .PAE_RST_N(PAE_RST_N), "
                     f".FFNODE_I(ffn_c{c}_{i}), .FFNODE_O({owire(c,i)}), "
                     f".PROG_DATA(CONFIG_DATA[{st} +: 1]));")
            L.append(f"    assign pa_o[{k}] = {owire(c,i)};")
            k += 1
    L.append("endmodule")

    open(f"{SD}/cone_{TAG}.v", "w").write("\n".join(L) + "\n")
    print(f"saved cone_{TAG}.v  CONFIG={n_cfg}bit "
          f"(skip={n_skip_bits} imux={n_imux_bits} pa={sum(widths)*2} ff={n_ff}@最下段)")
    return n_cfg


gen_verilog()
