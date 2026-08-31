#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_ext_uniform_all.py — 全42回路の「載る」構造を生成する。
   各回路専用に:
     - skip枠 = その回路の段固定skip実需要ちょうど(固定4/2/1でなく)
     - 外部入力 = 一律 N_EXT[c]=|PI| (全IMUX段, その回路のPI数)
   出力: src/cone_ext_uniform/<回路>.v (+ .png), 一覧 index.csv
 使い方: python3 gen_ext_uniform_all.py [回路名...]
 環境変数:
   FROM_RTL=1  元RTL(.v)から eblif を作り直してから構造生成する(rtl_to_eblif.py を使用)。
               出力先は results/verify/eblif_from_rtl/。
               ※eblifを作り直すと信号名が変わるため、既存の配置JSONは使えない(要・再配置)。
   EBDIR=<dir> eblif を探すディレクトリを明示指定
"""
import sys, os, glob, subprocess, re
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load
import sopa_paths as SP
SD = os.path.dirname(os.path.abspath(__file__))
FROM_RTL = os.environ.get("FROM_RTL") == "1"
MARGIN = int(os.environ.get("MARGIN", "0"))   # 非増加段(w[c]<=w[c-1])に +MARGIN 本。載らない回路の救済用
RS = os.environ.get("EBDIR") or os.path.join(SP.work_dir(), "eblif_from_rtl")
# ★2026-08-31: 生成物は src/ でなく results/ にまとめる（ソースと混ざらないように）
OUT = os.environ.get("OUTDIR") or os.path.join(SP.work_dir(), "cone_ext_uniform")
os.makedirs(OUT, exist_ok=True)
SKIP_CKT = {"ass13_tb"}


def pis_of(eb):
    for l in open(eb):
        if l.startswith('.inputs'):
            return set(l.split()[1:])
    return set()


def comb_po_cells(eb, cbo):
    """組合せPO(=出力のうちDFF Qでないもの)を出力するcboセルの集合。最下段(FF段)へ置く対象。"""
    pos = []; dffq = set(); conn = {}
    for l in open(eb):
        l = l.strip()
        if l.startswith('.outputs'): pos = l.split()[1:]
        elif l.startswith('.subckt DFF'):
            dffq.add(dict(t.split('=', 1) for t in l.split()[2:]).get('Q'))
        elif l.startswith('.conn'):
            pp = l.split()
            if len(pp) >= 3: conn[pp[2]] = pp[1]
    def rz(s):
        seen = set()
        while s in conn and s not in seen: seen.add(s); s = conn[s]
        return s
    res = set()
    for p in pos:
        if p in dffq: continue
        q = p if p in cbo else rz(p)
        if q in cbo and q not in dffq: res.add(q)
    return res


sel = [os.path.splitext(os.path.basename(a))[0] if a.endswith(".v") else a for a in sys.argv[1:]]

if FROM_RTL:                                  # 元RTL -> eblif を先に流す
    from rtl_to_eblif import rtl_to_eblif, resolve_rtl, RTL_DIR
    targets = sel or sorted(os.path.splitext(os.path.basename(p))[0]
                            for p in glob.glob(os.path.join(RTL_DIR, "*.v")))
    print(f"[FROM_RTL] {len(targets)}回路を RTL から再生成 (RTL_DIR={RTL_DIR})", flush=True)
    for ckt in targets:
        if ckt in SKIP_CKT: continue
        try:
            rtl_to_eblif(resolve_rtl(ckt), outdir=RS)
        except Exception as e:
            print(f"{ckt:16s} eblif生成 失敗: {e}", flush=True)
    print("", flush=True)

ebs = []
for d in sorted(glob.glob(os.path.join(RS, "*"))):
    if not os.path.isdir(d):
        continue
    ckt = os.path.basename(d)
    if ckt in SKIP_CKT or (sel and ckt not in sel):
        continue
    cand = glob.glob(os.path.join(d, f"mapped_{ckt}.v.eblif"))
    if cand:
        ebs.append((ckt, cand[0]))

print(f"回路数={len(ebs)}  OUT={OUT}\n", flush=True)
rows = []
for ckt, eb in ebs:
    try:
        logic, cbo, R, nff = load(eb)
        D = max(R.values()) + 1
        col = {o: (D - 1) - R[o] for o in cbo}
        for o in comb_po_cells(eb, cbo):     # 組合せPOを最下段(FF段,ff=1=通す前)へ移動→pa_o出力&FFfb内部帰還
            col[o] = D - 1
        widths = [Counter(col.values()).get(c, 0) for c in range(D)]     # 入力->FF
        # ★2026-08-31 追加: 幅0の段を作らない（最低1を保証する）。
        #   なぜ起きるか: 段0にセルが1個しか居らず、それが組合せPOだと、
        #     POを最下段へ移した結果 段0 が空になる（girl10 が該当。41回路中1件のみ）。
        #   幅0の段は「候補(前行)=[]」を生み、配置配線ツールのパーサが落ちる。
        #   ★なぜ「詰める」でなく「1を保証」か（2026-08-31 実験して判明）:
        #     段0は【IMUXを持たない】専用段で、PAが外部入力 I[] を直受けする
        #       PA pa_c0_0 (.PA_I_A(I[0]), .PA_I_B(I[1]), ...)   ← 選べない固定配線
        #     詰めると旧段1のPAが段0に降り、IMUX(FFfb/skip/EXT/定数を選ぶ)を失う。
        #     girl10 で config は 465→433 と減ったが、それは節約でなく能力の低下だった。
        #   よって空段は潰さず、幅1のスロットを1個だけ確保して段の構成を保つ。
        for c in range(D):
            if widths[c] == 0:
                widths[c] = 1
                print(f"{ckt:16s} ↳ 段{c}が空になったので幅1を確保した(D={D}は変えない)", flush=True)
        for c in range(1, D):                       # マージン: 非増加段(縮小+平坦)に +MARGIN 本
            if widths[c] <= widths[c - 1]: widths[c] += MARGIN
        nPI = len(pis_of(eb))
        # skip実需要 (行き先段c, 距離d)->本数
        dem = defaultdict(int)
        for c in logic:
            u = c['o']
            if u not in col:
                continue
            for s in c['srcs']:
                if s in cbo:
                    g = col[u] - col[s]
                    if g >= 2:
                        dem[(col[u], g)] += 1
        skipmap = ";".join(f"{c},{d},{n}" for (c, d), n in dem.items())
        next_ext = [0] + [nPI] * (D - 1)                                 # 段0は直受け, 以降 一律|PI|
        ff_to_in = ",".join(map(str, reversed(widths)))
        env = dict(os.environ, SKIPMAP=skipmap, NEXT=",".join(map(str, next_ext)),
                   NEXTTAG=f"{ckt}_uni")
        r = subprocess.run([sys.executable, "gen_cone_ext.py", ff_to_in],
                           cwd=SD, capture_output=True, text=True, env=env)
        mcfg = re.search(r'CONFIG=(\d+)bit', r.stdout)
        config = int(mcfg.group(1)) if mcfg else 0
        vsrc = os.path.join(SD, "cone_spindle_" + "-".join(map(str, reversed(widths))) + f"_{ckt}_uni.v")
        psrc = vsrc[:-2] + ".png"
        ok = os.path.exists(vsrc)
        if ok:
            os.replace(vsrc, os.path.join(OUT, f"{ckt}.v"))
        if os.path.exists(psrc):
            os.replace(psrc, os.path.join(OUT, f"{ckt}.png"))
        status = "OK" if ok else "GEN_FAIL"
        rows.append((ckt, len(cbo), D, nPI, sum(dem.values()), config, status))
        print(f"{ckt:16s} cells={len(cbo):4d} D={D:2d} |PI|={nPI:3d} skip需要={sum(dem.values()):4d} config={config:6d} {status}", flush=True)
        if not ok and r.stderr.strip():
            print("     └ err:", r.stderr.strip().splitlines()[-1][:160], flush=True)
    except Exception as e:
        rows.append((ckt, 0, 0, 0, 0, 0, f"EXC:{e}"))
        print(f"{ckt:16s} EXC {e}", flush=True)

# index.csv は**上書きせず更新**する。回路を絞って実行したときに他の回路の行を失わないため。
HDR = "circuit,cells,D,nPI,skip_demand,config_bit,status"
idx = os.path.join(OUT, "index.csv")
prev = {}
if os.path.exists(idx):
    for line in open(idx).read().splitlines()[1:]:
        if line.strip(): prev[line.split(",")[0]] = line
for r in rows:
    prev[str(r[0])] = ",".join(map(str, r))
with open(idx, "w") as f:
    f.write(HDR + "\n")
    for k in sorted(prev): f.write(prev[k] + "\n")
ok = sum(1 for r in rows if r[6] == "OK")
print(f"\n=== 生成 {ok}/{len(rows)}  出力: {OUT}  一覧: index.csv ===")
