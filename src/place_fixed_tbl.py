#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_fixed_tbl.py — place_fixed_skip_ext.py の【符号化だけ変えた】版（表制約）。2026-09-02。
 元: place_fixed_skip.py の複製＋外部入力(EXT)の段別枠チェック版。
 元の place_fixed_skip.py は変更しない。差分は「外部入力の段別枠 next_ext[c] を守るか静的判定」する点。
 - 段固定(col=D-1-R)なので、各段cが必要とする"相異なるPI数"は静的に確定。
   条件: 段c(1..D-1)の相異なるPI数 <= next_ext[c]。段0は外部入力を直受けするので対象外。
 - next_ext[c] は .v ヘッダ "N_EXT_LIST=[...]"(入力側->FF側) から読む。無ければ全0(=PI要求があれば不可)。
 使い方: python3 place_fixed_skip_ext.py <EBLIF> <CONE_V> [HOME_EBLIF]   環境: ATIME(秒, default120)
"""
import sys, os, re, json
from collections import defaultdict
from ortools.sat.python import cp_model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load, gen_pattern

EB, GRIDV = sys.argv[1], sys.argv[2]
HOME = sys.argv[3] if len(sys.argv) > 3 else None
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths)
# 外部入力の段別枠 next_ext (入力側->FF側)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D


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


def skip_demand(eblif):
    lg, cb, RR, _ = load(eblif)
    cl = {o: (D - 1) - RR[o] for o in cb}
    dem = defaultdict(int)
    for c in lg:
        u = c['o']
        if u not in cl:
            continue
        for s in c['srcs']:
            if s in cb:
                g = cl[u] - cl[s]
                if g >= 2:
                    dem[(cl[u], g)] += 1
    return dem


if HOME:
    skipbudget = skip_demand(HOME)
    BUDSRC = f"home={os.path.basename(HOME)}の実需要"
else:
    skipbudget = defaultdict(int)
    for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段', gtxt):
        skipbudget[(int(mm.group(2)), int(mm.group(3)))] += 1
    BUDSRC = ".v定義枠(4/2/1)"

PI = pis_of(EB)
logic, cbo, R, nff = load(EB)
maxR = max(R.values())
if maxR + 1 > D:
    print(f"結果: INFEASIBLE(段不足) 構造D={D} < 回路FF距離段{maxR+1}"); sys.exit()
col_of = {o: (D - 1) - R[o] for o in cbo}
for o in comb_po_cells(EB, cbo):     # 組合せPOを最下段(FF段)へ。後ろ向き辺はFFfbが吸収(cover/skip不要)
    col_of[o] = D - 1
bycol = defaultdict(list)
for o in cbo:
    bycol[col_of[o]].append(o)
print(f"{CKT}: セル{len(cbo)} / FF{nff} / D={D} / skip枠={BUDSRC} / next_ext={next_ext}", flush=True)
for col, cs in bycol.items():
    if len(cs) > widths[col]:
        print(f"結果: INFEASIBLE(容量) 段{col}: {len(cs)} > 幅{widths[col]}"); sys.exit()

# ---- 外部入力(EXT)枠チェック(静的): 段c(1..D-1)の相異なるPI数 <= next_ext[c] ----
pi_at = defaultdict(set)
for c in logic:
    u = c['o']
    if u not in col_of:
        continue
    for s in c['srcs']:
        if s in PI:
            pi_at[col_of[u]].add(s)
ext_over = [(c, len(pis), next_ext[c]) for c, pis in pi_at.items()
            if c >= 1 and len(pis) > next_ext[c]]
if ext_over:
    print(f"結果: INFEASIBLE(外部入力枠不足) 超過(段,相異なるPI需要,枠)={ext_over}")
    sys.exit()

# ---- skip需要(静的) ----
skipdemand = defaultdict(int)
edges1 = []
nskip = 0
for c in logic:
    u = c['o']
    if u not in col_of:
        continue
    for s in c['srcs']:
        if s in cbo:
            g = col_of[u] - col_of[s]
            if g == 1:
                edges1.append((s, u))
            elif g >= 2:
                nskip += 1
                skipdemand[(col_of[u], g)] += 1
over = [(k, d, n, skipbudget.get((k, d), 0)) for (k, d), n in skipdemand.items()
        if n > skipbudget.get((k, d), 0)]
if over:
    print(f"結果: INFEASIBLE(skip枠不足) 超過(段,距離,需要,枠)={over}  skip総数={nskip}")
    sys.exit()

cand = {col: gen_pattern(widths[col - 1], widths[col]) for col in range(1, D)}
m = cp_model.CpModel()
row = {o: m.NewIntVar(0, widths[col_of[o]] - 1, '') for o in cbo}
for col, cs in bycol.items():
    if len(cs) > 1:
        m.AddAllDifferent([row[o] for o in cs])

# ★2026-09-02 符号化の変更（place_fixed_tbl.py）:
#   旧: 辺1本につき「uが行r」×「sが候補行r'」の Bool を 幅×候補数 個作って OR で結ぶ
#   新: 辺1本につき表制約 AddAllowedAssignments([row[s], row[u]], 許可ペア) 1個
#   解く問題は同一。変数の数が 1/幅 程度になるので速くなる見込み（実測で確認する）
pairs = {}
for cu in range(1, D):
    pairs[cu] = [(rp, r) for r in range(widths[cu]) for rp in cand[cu][r]]
for s, u in edges1:
    m.AddAllowedAssignments([row[s], row[u]], pairs[col_of[u]])

sv = cp_model.CpSolver()
sv.parameters.max_time_in_seconds = int(os.environ.get("ATIME", "120"))
sv.parameters.num_search_workers = 8
st = sv.Solve(m)
print(f"結果: {sv.StatusName(st)} ({sv.WallTime():.0f}s)  gap1={len(edges1)} skip={nskip}"
      f"  外部入力需要(段:相異PI)={ {c: len(p) for c, p in sorted(pi_at.items())} }", flush=True)
if sv.StatusName(st) in ('FEASIBLE', 'OPTIMAL'):
    json.dump({'col': col_of, 'row': {o: sv.Value(row[o]) for o in cbo}},
              open(f'place_fixed_tbl_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_fixed_tbl_{CKT}.json")
