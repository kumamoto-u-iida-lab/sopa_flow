#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_skip_cone.py — cone構造(段幅可変)への配置配線(CP-SAT)。既存 place_skip.py の cone対応版(別ファイル)。

cone対応の差分:
  - N_COL=D, 段ごと幅 widths[行] を cone .v のヘッダ (widths(入力側->FF側)=[...]) から読む。
  - 各行(段)の本体数 <= widths[行]、row < widths[col]。
  - must(FFのD入力, 組合せPO)は FF可能な下3段(行 D-3..D-1) に置く(col >= FF_START)。
  - cand[行][PA] と skip枠は cone .v コメント(行表記)から読む。
座標: col=行(段,ASAP..ALAP,入力側0->FF側D-1) / row=列(幅方向)。※行列定義は行=段,列=幅。
使い方: python3 place_skip_cone.py <EBLIF> <CONE_V>
環境: ATIME(秒, default300)
"""
import sys, os, re, json
from collections import defaultdict
from ortools.sat.python import cp_model

CONST = {'$true', '$false', '$undef'}
EBLIF = sys.argv[1]
GRIDV = sys.argv[2]
CKT = os.path.basename(EBLIF).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')

# ---------- eblif ----------
cells, dffs, pis, pos = [], [], [], []
for l in open(EBLIF):
    l = l.strip()
    if l.startswith('.inputs'): pis = l.split()[1:]
    elif l.startswith('.outputs'): pos = l.split()[1:]
    elif l.startswith('.subckt cell'):
        p = dict(t.split('=', 1) for t in l.split()[2:])
        cells.append({'o': p['O_a'], 'srcs': [s for s in (p.get('I_a'), p.get('I_b')) if s and s not in CONST]})
    elif l.startswith('.subckt DFF'):
        dffs.append(dict(t.split('=', 1) for t in l.split()[2:]))
cr = {d['C'] for d in dffs} | {d['R'] for d in dffs}
logic = [c for c in cells if c['o'] not in cr]          # clk/rstは大域網(配置除外)
dff_q = {d['Q'] for d in dffs}
cbo = {c['o']: c for c in logic}
comb_pos = [p for p in pos if p not in dff_q]
# ★2026-08-31 変更: 組合せPOは【複製せず移動】する。
#   構造の最下段には FLIPFLOP_NODE (2to1MUX: 通す/登録) が付いていて、その出力は
#   pa_o(外部出力) と FFfb(全段の全IMUXの候補) の両方へ出る（girl10.v の実物で確認済み）。
#   よって POセル自身を最下段に置けば、外部出力にも内部の読み手にも同時に届き、
#   後ろ向きの辺にならない。→ 複製は不要（2026-08-04 の結論どおり）。
#   複製していた版は要らないセルを1個作り、構造の総スロットを1個超えて
#   INFEASIBLE になっていた（2026-08-30 に41回路で確認: セル数 = 総スロット + 1）。
must = {d['D'] for d in dffs if d['D'] in cbo} | {p for p in comb_pos if p in cbo}

# ---------- cone構造: widths / cand[行][PA] / skip枠 ----------
gtxt = open(GRIDV).read()
mw = re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt)
widths = [int(x) for x in mw.group(1).split(',')]
D = len(widths); N_COL = D; WMAX = max(widths)
# must(FF-D/PO)の許容段。既定=下3段(D-3..D-1)。環境変数 FFLAST=1 で最下段D-1ちょうどに固定
# (構造のFLIPFLOP_NODEは最下段のみ→順序回路の正しさにはD-1固定が正)。
FF_START = (D - 1) if os.environ.get("FFLAST") else max(1, D - 3)
cand = defaultdict(dict)
for mm in re.finditer(r'//\s*行(\d+)\s*PA(\d+):\s*候補\(前行\)=\s*\[([0-9,\s]*)\]', gtxt):
    cand[int(mm.group(1))][int(mm.group(2))] = [int(x) for x in mm.group(3).split(',')]
HOME = sys.argv[3] if len(sys.argv) > 3 else None    # 任意: 枠をhome回路の段固定skip需要から与える
if HOME:
    from place_greedy import load as _pgload
    _lg, _cb, _RR, _ = _pgload(HOME)
    _cl = {o: (D - 1) - _RR[o] for o in _cb}
    skipbudget = defaultdict(int)
    for _c in _lg:
        _u = _c['o']
        if _u not in _cl:
            continue
        for _s in _c['srcs']:
            if _s in _cb:
                _g = _cl[_u] - _cl[_s]
                if _g >= 2:
                    skipbudget[(_cl[_u], _g)] += 1
    BUDSRC = f"home={os.path.basename(HOME)}の段固定需要"
else:
    skipbudget = defaultdict(int)
    for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段', gtxt):
        skipbudget[(int(mm.group(2)), int(mm.group(3)))] += 1
    BUDSRC = ".v内蔵skip枠(構造の定義どおり)"
MAXSKIP = max([d for (_, d) in skipbudget], default=1)
print(f"  skip枠={BUDSRC}  MAXSKIP={MAXSKIP}", flush=True)

ff_slots = sum(widths[k] for k in range(FF_START, D))
print(f"{CKT}: セル{len(logic)} / must(FF-D,PO){len(must)} / D={D} widths={widths} / "
      f"FF枠(下{D-FF_START}段)={ff_slots} / MAXSKIP={MAXSKIP}", flush=True)
if len(must) > ff_slots:
    print(f"  ⚠ must{len(must)} > FF枠{ff_slots}: この構造では原理的に不可(FF枠不足)", flush=True)

# ---------- ASAP / ALAP ----------
ASAP = {}; rem = list(logic)
while rem:
    nx = []
    for c in rem:
        ss = [s for s in c['srcs'] if s in cbo]
        if all(s in ASAP for s in ss): ASAP[c['o']] = max([ASAP[s]+1 for s in ss] + [0])
        else: nx.append(c)
    rem = nx
dist = {o: 0 for o in must}
ch = True
while ch:
    ch = False
    for c in logic:
        nd = dist.get(c['o'])
        if nd is None: continue
        for s in c['srcs']:
            if s in cbo and dist.get(s, -1) < nd+1: dist[s] = nd+1; ch = True
ALAP = {o: N_COL-1-dist.get(o, 0) for o in cbo}

# ---------- CP-SAT ----------
m = cp_model.CpModel()
col = {o: m.NewIntVar(min(ASAP[o], N_COL-1), ALAP[o], '') for o in cbo}
for o in must: m.Add(col[o] >= FF_START)                 # FF可能な下3段へ
row = {o: m.NewIntVar(0, WMAX-1, '') for o in cbo}

# col==k のとき row < widths[k]
for o in cbo:
    for k in range(N_COL):
        if widths[k] < WMAX:
            ck = m.NewBoolVar('')
            m.Add(col[o] == k).OnlyEnforceIf(ck)
            m.Add(col[o] != k).OnlyEnforceIf(ck.Not())
            m.Add(row[o] < widths[k]).OnlyEnforceIf(ck)

# 同一列のセルは行が異なる
cl = list(cbo)
for ii in range(len(cl)):
    for jj in range(ii+1, len(cl)):
        a, b = cl[ii], cl[jj]
        if ASAP[a] > ALAP[b] or ASAP[b] > ALAP[a]: continue
        same = m.NewBoolVar('')
        m.Add(col[a] == col[b]).OnlyEnforceIf(same)
        m.Add(col[a] != col[b]).OnlyEnforceIf(same.Not())
        m.Add(row[a] != row[b]).OnlyEnforceIf(same)

# エッジ: gap=1(隣接候補) / gap>=2(skip枠, 行自由)
skip_use = defaultdict(list)
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s not in cbo: continue
        gap = m.NewIntVar(1, MAXSKIP, '')
        m.Add(gap == col[u] - col[s])
        is1 = m.NewBoolVar('')
        m.Add(gap == 1).OnlyEnforceIf(is1)
        m.Add(gap != 1).OnlyEnforceIf(is1.Not())
        for k in range(1, N_COL):
            ck = m.NewBoolVar('')
            m.Add(col[u] == k).OnlyEnforceIf(ck)
            m.Add(col[u] != k).OnlyEnforceIf(ck.Not())
            for r in range(widths[k]):
                ru = m.NewBoolVar('')
                m.Add(row[u] == r).OnlyEnforceIf(ru)
                m.Add(row[u] != r).OnlyEnforceIf(ru.Not())
                allowed = cand[k].get(r, [])
                lit = [is1, ck, ru]
                if allowed:
                    bvs = []
                    for rp in allowed:
                        bb = m.NewBoolVar('')
                        m.Add(row[s] == rp).OnlyEnforceIf(bb)
                        m.Add(row[s] != rp).OnlyEnforceIf(bb.Not())
                        bvs.append(bb)
                    m.AddBoolOr(bvs).OnlyEnforceIf(lit)
                else:
                    m.AddBoolOr([x.Not() for x in lit])
        for d in range(2, MAXSKIP+1):
            isd = m.NewBoolVar('')
            m.Add(gap == d).OnlyEnforceIf(isd)
            m.Add(gap != d).OnlyEnforceIf(isd.Not())
            for k in range(d, N_COL):
                ck = m.NewBoolVar('')
                m.Add(col[u] == k).OnlyEnforceIf(ck)
                m.Add(col[u] != k).OnlyEnforceIf(ck.Not())
                use = m.NewBoolVar('')
                m.AddBoolAnd([isd, ck]).OnlyEnforceIf(use)
                m.AddBoolOr([isd.Not(), ck.Not()]).OnlyEnforceIf(use.Not())
                skip_use[(k, d)].append(use)

for (k, d), uses in skip_use.items():
    m.Add(sum(uses) <= skipbudget.get((k, d), 0))

# 各段の本体数 <= widths[段]
for k in range(N_COL):
    bs = []
    for o in cbo:
        v = m.NewBoolVar('')
        m.Add(col[o] == k).OnlyEnforceIf(v)
        m.Add(col[o] != k).OnlyEnforceIf(v.Not())
        bs.append(v)
    m.Add(sum(bs) <= widths[k])

sv = cp_model.CpSolver()
sv.parameters.max_time_in_seconds = int(os.environ.get("ATIME", "300"))
sv.parameters.num_search_workers = 8
st = sv.Solve(m)
print("結果:", sv.StatusName(st), f"({sv.WallTime():.0f}s)", flush=True)
if sv.StatusName(st) in ('FEASIBLE', 'OPTIMAL'):
    w = defaultdict(int)
    for o in cbo: w[sv.Value(col[o])] += 1
    print("  本体の段分布(行0->D-1):", [w[k] for k in range(N_COL)], "/ 段幅:", widths, flush=True)
    used = defaultdict(int)
    for c in logic:
        u = c['o']
        for s in c['srcs']:
            if s in cbo:
                g = sv.Value(col[u]) - sv.Value(col[s])
                if g >= 2: used[g] += 1
    print("  skip使用(距離別):", dict(used), flush=True)
    json.dump({'col': {o: sv.Value(col[o]) for o in cbo}, 'row': {o: sv.Value(row[o]) for o in cbo}},
              open(f'place_skip_cone_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_skip_cone_{CKT}.json", flush=True)

    # ---- 使用部分の可視化 (構造レイアウト上に使用ノード/配線をハイライト) ----
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    def _xs(n): return [(i - (n - 1) / 2) * 1.0 for i in range(n)]
    cv = {o: sv.Value(col[o]) for o in cbo}
    rv = {o: sv.Value(row[o]) for o in cbo}
    fig, ax = plt.subplots(figsize=(max(6, WMAX * 0.5), 2.2 * D))
    # 全構造ノード(薄グレー)＋段ラベル
    for k in range(N_COL):
        X = _xs(widths[k])
        ax.scatter(X, [-k] * widths[k], s=16, color="#dcdcdc", zorder=1)
        ax.text(min(X) - 1.2, -k, f"stage{k}\nw={widths[k]}", ha="right", va="center",
                fontsize=8, color="#999999")
    # 使用エッジ(隣接=青 / skip=オレンジ)
    nskip = 0
    for c in logic:
        u = c['o']
        if u not in cv: continue
        xu = _xs(widths[cv[u]])[rv[u]]; yu = -cv[u]
        for s in c['srcs']:
            if s in cv:
                xsrc = _xs(widths[cv[s]])[rv[s]]; ysrc = -cv[s]
                g = cv[u] - cv[s]
                if g >= 2: nskip += 1
                ax.plot([xsrc, xu], [ysrc, yu],
                        color="#e8880c" if g >= 2 else "#4477aa",
                        lw=1.1, alpha=0.75, zorder=2)
    # 使用ノード(FF段=赤 / それ以外=青)
    for o in cbo:
        k = cv[o]; xo = _xs(widths[k])[rv[o]]; yo = -k
        ff = (k == N_COL - 1)
        ax.scatter([xo], [yo], s=110 if ff else 65,
                   color="#e8261c" if ff else "#2f5fb0", zorder=3)
    ax.axis("off")
    ax.set_title(f"{CKT} placed on structure  widths(input->FF)={widths}\n"
                 f"used {len(cbo)} nodes (red=FF stage, grey=unused) / "
                 f"edges: blue=adjacent, orange=skip({nskip})", fontsize=11)
    plt.tight_layout(); plt.savefig(f"place_skip_cone_{CKT}.png", dpi=130, bbox_inches="tight")
    print(f"  保存: place_skip_cone_{CKT}.png", flush=True)
