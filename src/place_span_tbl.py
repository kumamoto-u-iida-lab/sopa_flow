#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_span_tbl.py — 段固定SAT(place_fixed_tbl.py)の「行を少しだけ緩める」版。2026-10-05。

元の place_fixed_tbl.py は変更しない（別名で新規）。

用語: 行 h = FF側から数えた距離（h=0 が FF の行）。構造の段番号は D-1-h。
      h0 = 段固定のときの行（FF までの最長距離。組合せPOは 0）。
前提: 全部中継のネットリスト（段固定で全ての辺がちょうど1行差）。2行以上の辺があれば止める。

行の許し方（MODE）:
  fixed : h = h0（place_fixed_tbl.py と同じ問題。検算用）
  B     : h0=0 のセルは h=0。それ以外は h ∈ {h0, h0+1}（行の範囲を固定）
  A     : h0=0 のセルは h=0。辺ごとに「親は子の1つ上か2つ上」。h ∈ [h0, min(D-1, 子の上限+2 の最小)]
  どの MODE でも辺(親s→子u)は h(s)-h(u) = 1 + g（g=1 なら間の行に中継(FT)を置く）。
中継の置き方（FT）:
  edge  : 2行差の辺ごとに中継を1つ
  share : 親ごとに中継を1つ（2行差の子どうしで共有）
組合せPOのセルは段固定と同じく FF の行(h=0)に固定。外部入力(PI)の行ごとの枠は、行が動くので SAT の中で守る。

符号化（v3, 直接Bool版）:
  x[セル,行,列] = そのマスに置く。セルごとに ExactlyOne、マスごとに AtMostOne（セルと中継）。
  辺(親s→子u)ごとに g（中継を使う）を1つ。行の関係は線形:  行s=行u+1+g。
  候補表は「子がマス(h,k)にいる → 1つ上の行の候補列のどれかに 親(g=0) or 中継(g=1)」の節。
  中継 y[中継,行,列] は「中継がマスにいる → 親は中継の候補列のどれか」。
  （表制約で書くと CP-SAT が表の1行ごとに Bool を作り、girl10 で 5.9万変数に膨れたため。v1/v2 は不採用）
使い方: python3 place_span_tbl.py <EBLIF> <CONE_V>
環境: MODE(fixed/B/A, 既定B) FT(edge/share, 既定edge) CAND_RULE(既定now) ATIME(秒, 既定600) THREADS(既定8) PROBE(既定0)
"""
import sys, os, re, json
from collections import defaultdict
from ortools.sat.python import cp_model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load
from cand_rules import make_cand


def pis_of(eblif):
    for l in open(eblif):
        if l.startswith('.inputs'):
            return set(l.split()[1:])
    return set()


def comb_po_cells(eb, cbo):
    """組合せPO(出力のうちDFF Qでない)を出力するcboセル。最下段(FF段)へ置く対象。"""
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



EB, GRIDV = sys.argv[1], sys.argv[2]
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
MODE = os.environ.get("MODE", "B"); FT = os.environ.get("FT", "edge")
CAND_RULE = os.environ.get("CAND_RULE", "now")
assert MODE in ("fixed", "B", "A") and FT in ("edge", "share")
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D
W = lambda h: widths[D - 1 - h]                     # 行h の列数
OFF = {}; _o = 0
for h in range(D):                                  # 通し番号 = OFF[行] + 列
    OFF[h] = _o; _o += W(h)
NSLOT = _o

PI = pis_of(EB)
logic, cbo, R, nff = load(EB)
if max(R.values()) + 1 > D:
    print(f"結果: INFEASIBLE(段不足) D={D}"); sys.exit()
h0 = {o: R[o] for o in cbo}
for o in comb_po_cells(EB, cbo): h0[o] = 0
kids = defaultdict(list); edges = []
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s in cbo:
            g = h0[s] - h0[u]
            if g == 1: edges.append((s, u)); kids[s].append(u)
            elif g >= 2:
                print(f"結果: 対象外(2行以上の辺あり {s}->{u} 差{g})。全部中継のネットリストを使うこと"); sys.exit()
fixed0 = {o for o in cbo if h0[o] == 0}
if MODE == "fixed":
    dom = {o: [h0[o]] for o in cbo}
elif MODE == "B":
    dom = {o: [h0[o]] if o in fixed0 else [h for h in (h0[o], h0[o] + 1) if h <= D - 1] for o in cbo}
else:
    hmax = {}
    def hm(o):                                       # ずれの積み重ね: 子の上限 + 2 の最小
        if o in hmax: return hmax[o]
        hmax[o] = h0[o]
        v = h0[o] if o in fixed0 or not kids[o] else min(hm(k) + 2 for k in kids[o])
        hmax[o] = min(D - 1, v); return hmax[o]
    dom = {o: list(range(h0[o], hm(o) + 1)) for o in cbo}
# 親子で矛盾する行を前もって削る（子の行+1 以上 +2 以下に親が無い行は不要）
changed = True
while changed:
    changed = False
    for s, u in edges:
        ds = [h for h in dom[s] if any(1 <= h - x <= 2 for x in dom[u])]
        du = [h for h in dom[u] if any(1 <= x - h <= 2 for x in dom[s])]
        if ds != dom[s] or du != dom[u]: dom[s], dom[u] = ds, du; changed = True
if any(not d for d in dom.values()):
    print("結果: INFEASIBLE(行の範囲が空)"); sys.exit()
nmov = sum(1 for o in cbo if len(dom[o]) > 1)
print(f"{CKT}: セル{len(cbo)} / FF{nff} / D={D} / MODE={MODE} FT={FT} CAND_RULE={CAND_RULE} / 辺{len(edges)}"
      f" / 行を選べるセル {nmov}（選択肢 平均 {sum(len(d) for d in dom.values())/len(cbo):.2f} 行）", flush=True)

cand = {}                                            # cand[h][列] = 行h+1(上)の列の集合
for h in range(D - 1):
    sc = D - 1 - h
    cand[h] = make_cand(widths[sc - 1], widths[sc], CAND_RULE, row=sc)

m = cp_model.CpModel()
x = {}                                               # x[o][(h,k)]
cellat = defaultdict(list)                           # マス -> そこに置けるもの(Bool)
for o in cbo:
    x[o] = {(h, k): m.NewBoolVar('') for h in dom[o] for k in range(W(h))}
    m.AddExactlyOne(x[o].values())
    for hk, b in x[o].items(): cellat[hk].append(b)
inrow = lambda o, h: sum(x[o][(h, k)] for k in range(W(h))) if h in dom[o] else 0

ftrec = []                                           # (親, 中継のy辞書, 使うBool)
viarec = []                                          # (親, 子, g, 中継のy辞書)
relay_of = {}                                        # FT=share: 親 -> (y辞書, 使うBool)


def new_relay(s, rows):
    """親 s の中継。rows = 置ける行。y[(h,k)] と 使うBool を返す（Σy = use）"""
    y = {(h, k): m.NewBoolVar('') for h in rows for k in range(W(h))}
    use = m.NewBoolVar('')
    m.Add(sum(y.values()) == use)
    for (h, k), b in y.items():                      # 中継 → 親（親は行 h+1 の候補列）
        cl = [x[s][(h + 1, p)] for p in cand[h][k] if (h + 1, p) in x[s]]
        m.AddBoolOr(cl + [b.Not()])
        cellat[(h, k)].append(b)
    ftrec.append((s, y, use))
    return y, use


for s, u in edges:
    can2 = max(dom[s]) - min(dom[u]) >= 2
    g = m.NewBoolVar('') if can2 else None
    # 行の関係  行s = 行u + 1 + g
    for h in dom[u]:
        if g is None:
            if len(dom[u]) > 1 or len(dom[s]) > 1: m.Add(inrow(s, h + 1) >= inrow(u, h))
        else:
            m.Add(inrow(s, h + 1) >= inrow(u, h) - g)
            m.Add(inrow(s, h + 2) >= inrow(u, h) + g - 1)
    y = None
    if can2:
        rows = sorted({h + 1 for h in dom[u] if h + 2 in dom[s]})
        if FT == "edge":
            y, use = new_relay(s, rows); m.Add(use == g)
        else:
            if s not in relay_of:
                rr = sorted({h - 1 for h in dom[s] if h >= 1 and any(h - 2 == hu for hu in dom[u])})
                relay_of[s] = [None, None, set(), []]
            relay_of[s][2].update(rows); relay_of[s][3].append((u, g))
        viarec.append((s, u, g, None))
    # 候補表: 子がマス(h,k) → 1つ上(行h+1)の候補列に 親(g=0) / 中継(g=1)
    for (h, k), b in x[u].items():
        if h + 1 > D - 1: continue
        if FT == "edge" or not can2:
            par = [x[s][(h + 1, p)] for p in cand[h][k] if (h + 1, p) in x[s]]
            if g is None:
                m.AddBoolOr(par + [b.Not()])
            else:
                m.AddBoolOr(par + [b.Not(), g])
                ry = [y[(h + 1, p)] for p in cand[h][k] if y and (h + 1, p) in y]
                m.AddBoolOr(ry + [b.Not(), g.Not()])
if FT == "share":
    for s, (_, _, rows, ug) in relay_of.items():
        y, use = new_relay(s, sorted(rows))
        relay_of[s][0], relay_of[s][1] = y, use
        m.AddMaxEquality(use, [g for _, g in ug])
    for s, u in edges:
        if s not in relay_of: continue
        gg = [g for uu, g in relay_of[s][3] if uu == u]
        if not gg: continue                           # 1行差しかない辺は上で済み
        y = relay_of[s][0]
        for (h, k), b in x[u].items():
            if h + 1 > D - 1: continue
            par = [x[s][(h + 1, p)] for p in cand[h][k] if (h + 1, p) in x[s]]
            g = gg[0]
            m.AddBoolOr(par + [b.Not(), g])
            ry = [y[(h + 1, p)] for p in cand[h][k] if (h + 1, p) in y]
            m.AddBoolOr(ry + [b.Not(), g.Not()])
for hk, bs in cellat.items():
    if len(bs) > 1: m.AddAtMostOne(bs)
# 通し番号の AllDifferent も併用（行ごとの「セル数 > 列数」型の矛盾を一気に見抜くため。AtMostOne だけでは鳩の巣の証明が遅い）
_alld = []; _dm = NSLOT
for o in cbo:
    sl = m.NewIntVarFromDomain(cp_model.Domain.FromValues([OFF[h] + k for (h, k) in x[o]]), '')
    for (h, k), b in x[o].items(): m.Add(sl == OFF[h] + k).OnlyEnforceIf(b)
    _alld.append(sl)
for s_, y_, use_ in ftrec:
    sl = m.NewIntVarFromDomain(cp_model.Domain.FromValues([OFF[h] + k for (h, k) in y_] + [_dm]), '')
    for (h, k), b in y_.items(): m.Add(sl == OFF[h] + k).OnlyEnforceIf(b)
    m.Add(sl == _dm).OnlyEnforceIf(use_.Not()); _alld.append(sl); _dm += 1
m.AddAllDifferent(_alld)

# 外部入力の行ごとの枠（構造の段0は直受けで対象外）
used = {}
for c in logic:
    u = c['o']
    if u not in cbo: continue
    for p in c['srcs']:
        if p in PI:
            for h in dom[u]:
                if D - 1 - h == 0: continue
                if (p, h) not in used: used[p, h] = m.NewBoolVar('')
                m.Add(used[p, h] >= inrow(u, h))
for h in range(D):
    vs = [v for (p, hh), v in used.items() if hh == h]
    if vs: m.Add(sum(vs) <= next_ext[D - 1 - h])

sv = cp_model.CpSolver()
sv.parameters.max_time_in_seconds = int(os.environ.get("ATIME", "600"))
sv.parameters.num_search_workers = int(os.environ.get("THREADS", "8"))
sv.parameters.cp_model_probing_level = int(os.environ.get("PROBE", "0"))   # 前処理の probing を既定で切る（girl10 B 6→2秒、A 25→15秒）
st = sv.Solve(m); name = sv.StatusName(st)
extra = ""
if name in ("FEASIBLE", "OPTIMAL"):
    pos = {o: next(hk for hk, b in x[o].items() if sv.Value(b)) for o in cbo}
    ypos = lambda y: next(hk for hk, b in y.items() if sv.Value(b))
    ft = [[s_, OFF[ypos(y_)[0]] + ypos(y_)[1]] for s_, y_, use_ in ftrec if sv.Value(use_)]
    yof = {}
    for s_, y_, use_ in ftrec:
        if sv.Value(use_): yof.setdefault(s_, []).append(y_)
    via = []
    for s_, u_, g_, _ in viarec:
        if not sv.Value(g_): continue
        hu, ku = pos[u_]
        for y_ in yof[s_]:                             # 子の1つ上にあって候補に入る中継
            hy, ky = ypos(y_)
            if hy == hu + 1 and ky in cand[hu][ku]: via.append([s_, u_, OFF[hy] + ky]); break
    nup = sum(1 for o in cbo if pos[o][0] != h0[o])
    extra = f"  上げたセル {nup} / 中継 {len(ft)}"
    json.dump({'h': {o: pos[o][0] for o in cbo}, 'slot': {o: OFF[pos[o][0]] + pos[o][1] for o in cbo},
               'MODE': MODE, 'FT': FT, 'ft': ft, 'via': via},
              open(f'place_span_{MODE}_{FT}_{CKT}.json', 'w'), ensure_ascii=False)
print(f"結果: {name} ({sv.WallTime():.0f}s){extra}", flush=True)
