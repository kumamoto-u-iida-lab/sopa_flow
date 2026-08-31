#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_config_verilog.py — 配置結果(json)→ CONFIG_DATA計算 → Formality用の構成済みVerilog(Impl)出力。
   段固定(自構造)配置を想定(FF-Dが最下段/FF段)。FF出力は各IMUXに専用フィードバック(FFfb)として入る(EXT不使用)。
   IMUX入力順: cover候補 + skip + FFfb(全FF出力) + EXT(外部入力PI) + 定数2。
   使い方: python3 gen_config_verilog.py <EBLIF> <CONE_V> <PLACE_JSON> [OUT_V]
   環境変数: CFGPORT=1 … CONFIG_DATA を焼き込まず外部ポートにする(案A: tbから並列に与える)
             SERIAL=1  … 既存eFPGAと同じシリアル書き込み口(CONF_*)を付ける(案B)
   出力: <OUT_V> / <回路>.bit (0-1のASCII 1行, 既存eFPGAと同形式) / <回路>_io.txt (I/O対応表)
"""
import sys, os, re, json, math
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import gen_pattern

EB, GRIDV, PJSON = sys.argv[1], sys.argv[2], sys.argv[3]
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
OUT = sys.argv[4] if len(sys.argv) > 4 else f"impl_{CKT}.v"
CFGPORT = os.environ.get("CFGPORT") == "1"
SERIAL = os.environ.get("SERIAL") == "1"      # 案B: 既存eFPGAと同じシリアル書き込み口を付ける
if SERIAL: CFGPORT = False                    # CONFIG_DATAは内部でシフトレジスタが作る

# 既存eFPGAの CONF_FF_TILE 相当。プロトコルは先輩tb(tb_addsub.v)から読み取ったものに合わせている:
#   CONF_RESETL: 0->1 でリセット解除 / CONF_MODE=1 の間 CONF_CLK立ち上がりで CONF_IN を1bitずつ取り込む
#   MSB(=CONFIG_DATA[NBIT-1])から先に送る / CONF_MODE=0 の直後に CONF_E=1 で有効化(追加クロック無し)
CONF_SHIFT_MODULE = """
module CONF_SHIFT #(parameter NBIT = 1) (
    input  wire            CONF_CLK,     // 書き込みクロック
    input  wire            CONF_RESETL,  // active-low リセット
    input  wire            CONF_MODE,    // 1=シフト中
    input  wire            CONF_IN,      // 1bitずつ入ってくる(MSBから)
    input  wire            CONF_E,       // 1=設定を有効化
    output wire            CONF_OUT,     // デイジーチェーン用(押し出されるbit)
    output wire [NBIT-1:0] CONFIG_DATA   // 論理部へ
);
    reg [NBIT-1:0] shft;
    always @(posedge CONF_CLK or negedge CONF_RESETL)
        if (!CONF_RESETL)   shft <= {NBIT{1'b0}};
        else if (CONF_MODE) shft <= {shft[NBIT-2:0], CONF_IN};
    // CONF_E=0 の間は論理部に設定が漏れない(シフト途中の値で回路が暴れない)
    assign CONFIG_DATA = CONF_E ? shft : {NBIT{1'b0}};
    assign CONF_OUT    = shft[NBIT-1];
endmodule
"""
SELW = lambda n: max(1, math.ceil(math.log2(n))) if n > 1 else 1
# skip の行選択ビット数。出発段の幅が1なら直結でmuxが無いので0bit(gen_cone_ext の SKW と同じ規則)。
SKW = lambda n: 0 if n <= 1 else SELW(n)
CONST = {'$true', '$false', '$undef'}

# ---- 構造 .v: widths / next_ext / skip枠 / FF段 ----
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths); Wmax = widths[0]
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D
skips = defaultdict(list)
for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段飛び\)\s*#(\d+)', gtxt):
    skips[int(mm.group(2))].append((int(mm.group(3)), int(mm.group(4))))
def skips_at(c): return skips.get(c, [])
# FF段: FLIPFLOP_NODE ff_c{c}_ の段を集める
FFSTAGES = sorted(set(int(m) for m in re.findall(r'FLIPFLOP_NODE ff_c(\d+)_', gtxt)))
if not FFSTAGES: FFSTAGES = [D - 1]
n_ff = sum(widths[c] for c in FFSTAGES)
# FF出力の順序(=pa_o index=FFfbバス位置): for c in FFSTAGES for i in widths[c]
ff_index = {}; _k = 0
for c in FFSTAGES:
    for i in range(widths[c]):
        ff_index[(c, i)] = _k; _k += 1
patterns = [gen_pattern(widths[s], widths[s + 1]) for s in range(D - 1)]

# ---- CONFIG_DATA レイアウト (gen_cone_ext と同順: skip→imux→pa→ff) ----
pos = 0; skip_cfg = {}
for c in range(1, D):
    for (dist, j) in skips_at(c):
        skip_cfg[(c, dist, j)] = (pos, SKW(widths[c - dist])); pos += SKW(widths[c - dist])
imux_cfg = {}
for c in range(1, D):
    nin = len(skips_at(c))
    for i in range(widths[c]):
        n = len(patterns[c - 1][i]) + nin + n_ff + next_ext[c] + 2   # ★ +n_ff (FFfb)
        for port in ('ia', 'ib'):
            imux_cfg[(c, i, port)] = (pos, SELW(n), n); pos += SELW(n)
pa_cfg = {}
for c in range(D):
    for i in range(widths[c]):
        pa_cfg[(c, i)] = pos; pos += 2
ff_cfg = {}
for c in FFSTAGES:
    for i in range(widths[c]):
        ff_cfg[(c, i)] = pos; pos += 1
n_cfg = pos

# ---- eblif ----
cells = {}; dffs = []; pis = []; pos_out = []; conn = {}
lines = open(EB).read().splitlines(); i = 0
while i < len(lines):
    l = lines[i].strip()
    if l.startswith('.inputs'): pis = l.split()[1:]
    elif l.startswith('.outputs'): pos_out = l.split()[1:]
    elif l.startswith('.subckt cell'):
        p = dict(t.split('=', 1) for t in l.split()[2:]); mode = None
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('.param MODE'):
            mode = lines[i + 1].strip().split()[-1]; i += 1
        cells[p['O_a']] = {'I_a': p.get('I_a'), 'I_b': p.get('I_b'), 'MODE': mode}
    elif l.startswith('.subckt DFF'):
        p = dict(t.split('=', 1) for t in l.split()[2:])
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('.param'): i += 1
        dffs.append(p)
    elif l.startswith('.conn'):
        pp = l.split()
        if len(pp) >= 3: conn[pp[2]] = pp[1]
    i += 1
def rz(s):
    seen = set()
    while s in conn and s not in seen:
        seen.add(s); s = conn[s]
    return s
dff_q = {d['Q'] for d in dffs}

# ---- クロック/リセットの極性を eblif から判定 ----
# PA: O = (I_a & (I_b ^ p0)) ^ p1。MODE文字列 m は m[1]->PROG_DATA[0](=p0), m[0]->PROG_DATA[1](=p1)。
# yosysは RTL の negedge clk / active-high rst を DFF_PN0(posedge C / clear=!R) に写すため、
# C や R の手前にインバータセルを挿す。それを辿って ~ の有無を決める(定数で仮定しない)。
def unit_of(s):
    """s を作るセルがバッファ/インバータなら (入力信号, 反転か)。2入力/定数なら None。"""
    c = cells.get(s)
    if not c or not c['MODE']: return None
    p1, p0 = int(c['MODE'][0]), int(c['MODE'][1])
    if   c['I_b'] == '$true':  g = 1 ^ p0
    elif c['I_b'] == '$false': g = 0 ^ p0
    else: return None                       # 本当に2入力で使っている
    if g == 0: return None                  # I_a が消えて定数になる
    return c['I_a'], bool(p1)

def polarity(s, depth=32):
    """s を PI まで遡って (根の信号名, 反転しているか) を返す。"""
    inv = False
    for _ in range(depth):
        s = rz(s)
        u = unit_of(s)
        if u is None: return s, inv
        s, i = u; inv ^= i
    return s, inv

place = json.load(open(PJSON)); col = place['col']; row = place['row']

# ---- DFF Q -> FF出力スロット(=pa_o index=FFfb位置) ----
ffidx_of_q = {}   # DFF Q名 -> ff_index
for d in dffs:
    dcell = rz(d['D'])
    if dcell in col and (col[dcell], row[dcell]) in ff_index:
        ffidx_of_q[d['Q']] = ff_index[(col[dcell], row[dcell])]

# ---- EXTマップ: stage>=1で外部から読む「データPI」だけ(DFF-QはFFfbで来るので除外) ----
ext_signals = []
for o, info in cells.items():
    if o not in col or col[o] == 0: continue
    for s in (info['I_a'], info['I_b']):
        if s is None: continue
        s = rz(s)
        if s in col or s in CONST or s in dff_q or s in ('clk', 'rst'): continue
        if s not in ext_signals: ext_signals.append(s)
ext_idx = {s: k for k, s in enumerate(ext_signals)}
maxext = max(next_ext)
assert len(ext_signals) <= maxext, f"EXT不足: 需要{len(ext_signals)} > 枠{maxext}"

# ---- config bit配列 ----
bits = ['0'] * n_cfg
def setv(start, width, value):
    for k in range(width): bits[start + k] = format(value, f'0{width}b')[::-1][k]

dff_dcells = {rz(d['D']) for d in dffs}   # 登録(ff=0)セル。FFfbは登録値を運ぶ
warn = []; Iwire = {}; skip_use_count = defaultdict(int)
for o, info in cells.items():
    if o not in col: continue
    c = col[o]; i = row[o]
    base = pa_cfg[(c, i)]; mode = info['MODE'] or '00'
    bits[base] = mode[1]; bits[base + 1] = mode[0]
    for port, s in [('ia', info['I_a']), ('ib', info['I_b'])]:
        if s is None: continue
        s = rz(s)
        if c == 0:                                  # stage0はI[]直受け(IMUX無し)
            Iwire[2 * i + (0 if port == 'ia' else 1)] = s
            continue
        st, w, ntot = imux_cfg[(c, i, port)]
        cover = patterns[c - 1][i]; nbase = len(cover); sk = skips_at(c); nskin = len(sk)
        base_ff = nbase + nskin                     # FFfbの開始位置
        base_ext = base_ff + n_ff                   # EXTの開始位置
        base_const = base_ext + next_ext[c]         # 定数の開始位置
        sel = None
        if s in col:                                # 配置セル(親)
            cp, rp = col[s], row[s]
            if (cp, rp) in ff_index:                # ★FF段の配置セル → FFfb経由(cover/skip不要, 後ろ向き辺OK)
                sel = base_ff + ff_index[(cp, rp)]
                if s in dff_dcells:                 # 登録セルを組合せ読み=FFfbは登録値→1cycleずれの恐れ(要pre-FF/2to1)
                    warn.append(f"DFF-D組合せ読み(登録値で代用): {o}<-{s}")
            else:
                gap = c - cp
                if gap == 1:
                    if rp in cover: sel = cover.index(rp)
                    else: warn.append(f"cover候補外: {o}<-親行{rp}")
                else:
                    avail = [(dd, jj) for (dd, jj) in sk if dd == gap]
                    j = skip_use_count[(c, gap)]
                    if j < len(avail):
                        _, jj = avail[j]; skip_use_count[(c, gap)] += 1
                        ss, sw = skip_cfg[(c, gap, jj)]; setv(ss, sw, rp)
                        sel = nbase + sk.index((gap, jj))
                    else: warn.append(f"skip枠不足: {o} 段{c} 距離{gap}")
        elif s in dff_q:                            # DFF-Q -> FFfbバス
            if s in ffidx_of_q: sel = base_ff + ffidx_of_q[s]
            else: warn.append(f"DFF-Q未配置: {o}<-{s}")
        elif s in CONST:
            sel = base_const + (1 if s == '$true' else 0)
        elif s in ext_idx:                          # データPI -> EXT
            sel = base_ext + ext_idx[s]
        else:
            warn.append(f"未分類source: {o} <- {s}")
        if sel is not None: setv(st, w, sel)
# FFビット: FF段。DFF-Dセル=登録(0)/他=パススルー(1)
dff_dcells = {rz(d['D']) for d in dffs}
for c in FFSTAGES:
    for i in range(widths[c]):
        occ = [o for o in col if col[o] == c and row[o] == i]
        bits[ff_cfg[(c, i)]] = '0' if any(o in dff_dcells for o in occ) else '1'

# ---- 出力信号 -> pa_o(FF出力) index ----
def producer_slot(p):
    if p in ffidx_of_q: return ffidx_of_q[p]        # DFF Q(登録)
    q = p if p in cells else rz(p)                  # 組合せ: pを出力するセル
    if q in col and (col[q], row[q]) in ff_index: return ff_index[(col[q], row[q])]
    return None
out_slot = {p: producer_slot(p) for p in pos_out}
for p, s in out_slot.items():
    if s is None: warn.append(f"出力未対応(FF段に無い): {p}")

# ---- CLK / PAE_RST_N に何を繋ぐか (DFFのC/Rの極性から決定) ----
# FLIPFLOP_NODE は posedge CLK / PAE_RST_N==0でクリア。DFF_PN0 も posedge C / clear=!R なので、
# C と R をそのまま(極性込みで)繋げばよい。
def port_expr(sigs, dflt):
    got = {("~" if inv else "") + base for base, inv in (polarity(s) for s in sigs)}
    if len(got) > 1: warn.append(f"{dflt}の極性が不統一: {sorted(got)}")
    return sorted(got)[0] if got else dflt
clk_expr = port_expr([d['C'] for d in dffs], 'clk')
rst_expr = port_expr([d['R'] for d in dffs], 'rst')

print(f"{CKT}: D={D} FF段={FFSTAGES} n_ff={n_ff} CONFIG={n_cfg}bit / EXT需要(PI){len(ext_signals)}(枠{maxext}) / skip使用={dict(skip_use_count)}")
print(f"  クロック/リセット(eblifから判定): CLK<={clk_expr}  PAE_RST_N<={rst_expr}")
print(f"  警告: {len(warn)}件" + (" -> " + "; ".join(warn[:5]) if warn else ""))

# ---- Impl Verilog 出力 ----
cfgconst = "".join(reversed(bits))
data_pi = [p for p in pis if p not in ('clk', 'rst')]
def feed(s):   # stage0のI[]用: DFF-Qはpa_o, PIは名前, 定数はリテラル
    if s is None or s == '$false': return "1'b0"
    if s == '$true': return "1'b1"
    if s in dff_q and s in ffidx_of_q: return f"pa_o[{ffidx_of_q[s]}]"
    if s in data_pi: return s
    return "1'b0"
buses = defaultdict(int); scalars = []
for p in pos_out:
    m = re.match(r'(.+)\[(\d+)\]$', p)
    if m: buses[m.group(1)] = max(buses[m.group(1)], int(m.group(2)))
    else: scalars.append(p)
outports = [f"output wire [{w}:0] {b}" for b, w in buses.items()] + [f"output wire {s}" for s in scalars]
L = []
L.append(f"// Impl: {CKT} on {os.path.basename(GRIDV)} (auto-config, FF feedback in IMUX). CONFIG={n_cfg}bit")
if SERIAL: L.append(CONF_SHIFT_MODULE)
L.append(f"module {CKT}_impl (input wire clk, input wire rst, "
         + ", ".join(f"input wire {p}" for p in data_pi) + ", " + ", ".join(outports)
         + (f", input wire [{n_cfg-1}:0] CONFIG_DATA" if CFGPORT else "")
         + (", input wire CONF_CLK, input wire CONF_RESETL, input wire CONF_MODE,"
            " input wire CONF_IN, input wire CONF_E, output wire CONF_OUT" if SERIAL else "")
         + ");")
if SERIAL:
    L.append(f"    wire [{n_cfg-1}:0] CONFIG_DATA;")
    L.append(f"    CONF_SHIFT #(.NBIT({n_cfg})) u_conf (.CONF_CLK(CONF_CLK), .CONF_RESETL(CONF_RESETL),"
             f" .CONF_MODE(CONF_MODE), .CONF_IN(CONF_IN), .CONF_E(CONF_E), .CONF_OUT(CONF_OUT),"
             f" .CONFIG_DATA(CONFIG_DATA));")
if Wmax: L.append(f"    wire [{2*Wmax-1}:0] I;")     # width[0]=0(段0が空)ならIバス省略
L.append(f"    wire [{n_ff-1}:0] pa_o;")
if maxext: L.append(f"    wire [{maxext-1}:0] EXT;")
for k in range(2 * Wmax):
    L.append(f"    assign I[{k}] = {feed(Iwire.get(k))};")
for s, k in ext_idx.items():
    L.append(f"    assign EXT[{k}] = {feed(s)};")   # データPIのみ(DFF-QはFFfbで内部帰還)
for p in pos_out:
    s = out_slot[p]
    L.append(f"    assign {p} = " + (f"pa_o[{s}];" if s is not None else "1'b0;  // 未対応"))
L.append(f"    cone u_cone (.CLK({clk_expr}), .PAE_RST_N({rst_expr}), "
         + (".I(I), " if Wmax else "")
         + (".EXT(EXT), " if maxext else "")
         + f".pa_o(pa_o), .CONFIG_DATA({'CONFIG_DATA' if (CFGPORT or SERIAL) else f'{n_cfg}' + chr(39) + 'b' + cfgconst}));")
L.append("endmodule")
open(OUT, "w").write("\n".join(L) + "\n")
print(f"  Impl出力: {OUT}" + ("  (CONF_*でシリアル書き込み=案B)" if SERIAL else "  (CONFIG_DATAは外部ポート=案A)" if CFGPORT else "  (CONFIG焼き込み)"))

# ---- .bit 出力 (既存手法と同形式: 0/1のASCII 1行・改行なし・長さ=config幅) ----
OD = os.path.dirname(os.path.abspath(OUT))
bitfile = os.path.join(OD, f"{CKT}.bit")
open(bitfile, "w").write(cfgconst)          # 先頭文字 = CONFIG_DATA[n-1] (MSB first)
print(f"  bitstream: {bitfile}  ({n_cfg}bit, 先頭がCONFIG_DATA[{n_cfg-1}])")

# ---- I/O 対応表 (tb がどのポートに何を繋ぐかの根拠) ----
iofile = os.path.join(OD, f"{CKT}_io.txt")
M = [f"# {CKT}: SoPA I/O マップ  (構造={os.path.basename(GRIDV)}, CONFIG={n_cfg}bit)",
     f"CLK        <= {clk_expr}",
     f"PAE_RST_N  <= {rst_expr}",
     f"# 入力: 段0は I[] で直受け, 段1以降は EXT[] 経由",
     f"I_WIDTH    = {2*Wmax}", f"EXT_WIDTH  = {maxext}", f"PA_O_WIDTH = {n_ff}"]
for k in range(2 * Wmax):
    M.append(f"I[{k}]      <= {feed(Iwire.get(k))}")
for s, k in sorted(ext_idx.items(), key=lambda t: t[1]):
    M.append(f"EXT[{k}]    <= {s}")
M.append("# 出力: pa_o(FF段出力) のどのスロットか")
for p in pos_out:
    M.append(f"{p} <= " + (f"pa_o[{out_slot[p]}]" if out_slot[p] is not None else "未対応"))
open(iofile, "w").write("\n".join(M) + "\n")
print(f"  I/Oマップ : {iofile}")
