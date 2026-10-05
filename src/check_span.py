#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_span.py — place_span_tbl.py の配置結果(json)を、ソルバと独立に検算する。2026-10-05。
使い方: python3 check_span.py <EBLIF> <CONE_V> <place_span_*.json>   環境: CAND_RULE(既定now)
確かめること: ①各マスに1つだけ ②辺は1行差なら候補表どおり、2行差なら親→中継→子が候補表どおり
              ③FF の行のセルは h=0 ④外部入力の行ごとの枠
"""
import sys, os, re, json
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load
from cand_rules import make_cand

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


EB, GRIDV, JS = sys.argv[1:4]
CAND_RULE = os.environ.get("CAND_RULE", "now")
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D
OFF = {}; o_ = 0
for h in range(D):
    OFF[h] = o_; o_ += widths[D - 1 - h]
def pos(sl):                                          # slot -> (行h, 列)
    for h in range(D):
        if OFF[h] <= sl < OFF[h] + widths[D - 1 - h]: return h, sl - OFF[h]
    raise ValueError(sl)
cand = {h: make_cand(widths[D - 2 - h], widths[D - 1 - h], CAND_RULE, row=D - 1 - h) for h in range(D - 1)}
ok = lambda hp, cp, hc, cc: hp == hc + 1 and cp in cand[hc][cc]

J = json.load(open(JS)); H = J['h']; SL = J['slot']
logic, cbo, R, _ = load(EB)
for o in comb_po_cells(EB, cbo): R[o] = 0          # 組合せPOは FF の行（place_span_tbl.py と同じ h0）
pis = set()
for l in open(EB):
    if l.startswith('.inputs'): pis = set(l.split()[1:])
err = []
used = Counter(SL.values()) + Counter(t for _, t in J['ft'])
err += [f"マス重複 slot{k}×{n}" for k, n in used.items() if n > 1]
for o in cbo:
    if pos(SL[o])[0] != H[o]: err.append(f"{o}: 行の記録不一致")
    if R[o] == 0 and H[o] != 0: err.append(f"{o}: FF 直結なのに行{H[o]}")
fts = defaultdict(set)
for s, t in J['ft']: fts[s].add(t)
via = {(s, u): e for s, u, e in J['via']}
ngap = Counter()
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s not in cbo or R[s] - R[u] != 1: continue  # 段固定で1行差だった辺だけが対象（逆向きはFFfb）
        hs, cs = pos(SL[s]); hu, cu = pos(SL[u]); g = hs - hu; ngap[g] += 1
        if g == 1:
            if not ok(hs, cs, hu, cu): err.append(f"{s}->{u}: 候補表に無い")
        elif g == 2:
            e = via.get((s, u))
            if e is None or e not in fts[s]: err.append(f"{s}->{u}: 2行差なのに中継なし"); continue
            he, ce = pos(e)
            if not (ok(hs, cs, he, ce) and ok(he, ce, hu, cu)): err.append(f"{s}->{u}: 中継経由が候補表に無い")
        else:
            err.append(f"{s}->{u}: 行の差 {g}")
pi_at = defaultdict(set)
for c in logic:
    if c['o'] in cbo:
        for p in c['srcs']:
            if p in pis and D - 1 - H[c['o']] >= 1: pi_at[H[c['o']]].add(p)
err += [f"外部入力枠超過 行{h}: {len(p)}>{next_ext[D-1-h]}" for h, p in pi_at.items() if len(p) > next_ext[D - 1 - h]]
print(f"検算: 辺の行差 {dict(ngap)} / 中継 {len(J['ft'])} / 上げたセル {sum(1 for o in cbo if H[o] != R[o])}"
      f" / 誤り {len(err)}" + ("".join("\n  " + x for x in err[:10])))
