#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_greedy.py — 逆順Kuhn貪欲による軽量配置(SAT不使用)。place_skip_cone.py の代替。
 段(col) = FF距離レベル (col=D-1-R) に固定、行(row)を段ごと二部マッチング(FF側→入力側)。
 skipは|ΔR|>=2のエッジのみ(行自由=無拘束)。gap=1は候補表(A_kカバー)で張る。
 構造の幅は cone.v ヘッダ (widths(入力側->FF側)=[...]) から読む。
 使い方: python3 place_greedy.py <EBLIF> <CONE_V>
"""
import sys, os, re
from collections import Counter, defaultdict
CONST = {'$true', '$false', '$undef'}


def gen_pattern(n_src, n_dst):
    N = n_dst; cand = {j: [] for j in range(n_dst)}; cur = 0
    for k in range(1, n_src + 1):
        a = min(N, (2 * N) // k)
        for _ in range(a):
            cand[cur % n_dst].append(k - 1); cur += 1
    return [sorted(set(cand[j])) for j in range(n_dst)]


def kuhn(cells, feas):
    sys.setrecursionlimit(200000)
    match_row = {}
    def aug(c, seen):
        for r in feas[c]:
            if r in seen: continue
            seen.add(r)
            if r not in match_row or aug(match_row[r], seen):
                match_row[r] = c; return True
        return False
    for c in cells:
        if not aug(c, set()):
            return None
    return {c: r for r, c in match_row.items()}


def load(eb):
    cells = []; dffs = []; pos = []
    for l in open(eb):
        s = l.strip()
        if s.startswith('.outputs'): pos = s.split()[1:]
        elif s.startswith('.subckt DFF'): dffs.append(dict(t.split('=', 1) for t in s.split()[2:]))
        elif s.startswith('.subckt cell'):
            p = dict(t.split('=', 1) for t in s.split()[2:])
            cells.append({'o': p['O_a'], 'srcs': [x for x in (p.get('I_a'), p.get('I_b')) if x and x not in CONST]})
    cr = {d['C'] for d in dffs} | {d['R'] for d in dffs}
    logic = [c for c in cells if c['o'] not in cr]; cbo = {c['o']: c for c in logic}
    sinks = set(pos) | {d['D'] for d in dffs}
    fo = {}
    for c in logic:
        for s in c['srcs']:
            if s in cbo: fo.setdefault(s, []).append(c['o'])
    memo = {}
    def rev(o):
        if o in memo: return memo[o]
        memo[o] = 0; ch = fo.get(o, [])
        v = 0 if o in sinks else (1 + max(rev(x) for x in ch) if ch else 0)
        if ch and o in sinks: v = 1 + max(rev(x) for x in ch)
        memo[o] = v; return v
    R = {c['o']: rev(c['o']) for c in logic}
    return logic, cbo, R, len(dffs)


def main():
    EB, GRIDV = sys.argv[1], sys.argv[2]
    CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
    gtxt = open(GRIDV).read()
    widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
    D = len(widths)                                   # 入力側->FF側
    logic, cbo, R, nff = load(EB)
    maxR = max(R.values())
    if maxR + 1 > D:
        print(f"{CKT}: 構造が浅い(段数D={D} < 回路のFF距離段{maxR+1}) → 不可"); return
    col_of = {c['o']: (D - 1) - R[c['o']] for c in logic}
    bycol = defaultdict(list)
    for c in logic:
        bycol[col_of[c['o']]].append(c['o'])
    print(f"{CKT}: セル{len(logic)} / FF{nff} / D={D} widths(入力->FF)={widths}", flush=True)
    for col, cs in bycol.items():
        if len(cs) > widths[col]:
            print(f"  容量NG 段{col}: {len(cs)} > 幅{widths[col]}  -> INFEASIBLE(容量)"); return
    cand = {col: gen_pattern(widths[col - 1], widths[col]) for col in range(1, D)}
    children = defaultdict(list)
    for c in logic:
        v = c['o']; cv = col_of[v]
        for s in c['srcs']:
            if s in cbo and cv - col_of[s] == 1:
                children[s].append(v)
    rowassign = {}; nskip = 0
    for c in logic:
        for s in c['srcs']:
            if s in cbo and col_of[c['o']] - col_of[s] >= 2:
                nskip += 1
    for col in range(D - 1, -1, -1):
        cells = bycol[col]
        if not cells:
            continue
        feas = {}
        for u in cells:
            s = set(range(widths[col]))
            for v in children[u]:
                s &= set(cand[col + 1][rowassign[v]])
            feas[u] = sorted(s)
            if not s:
                print(f"  結果: INFEASIBLE(貪欲)  段{col}で詰まり(a:置ける行が空)"); return
        mm = kuhn(cells, feas)
        if mm is None:
            print(f"  結果: INFEASIBLE(貪欲)  段{col}で詰まり(b:Hall違反)"); return
        rowassign.update(mm)
    print(f"  結果: FEASIBLE(貪欲) 全段配置OK  skip(gap>=2)={nskip}本", flush=True)
    import json
    json.dump({'col': {o: col_of[o] for o in cbo}, 'row': rowassign},
              open(f'place_greedy_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_greedy_{CKT}.json")


if __name__ == "__main__":
    main()
