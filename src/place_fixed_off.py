#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_fixed_off.py — place_fixed_tbl.py に「段オフセット」だけを足した版。2026-09-26。

元の place_fixed_tbl.py は一切変更していない（複製して別名。既存結果の再現性のため）。

差分は1点のみ:
  col_of[o] = (D - 1 - OFFSET) - R[o]        # 既定 OFFSET=0 なら place_fixed_tbl.py と完全に同一
  組合せPOセルも D - 1 - OFFSET へ固定

狙い（2026-09-26 小幡先生の着想）:
  段を「範囲で自由に」すると探索空間が爆発して UNKNOWN になる（全体SAT版 FFSPAN=3 で threediff が
  600秒でも未解決だった）。一方、段固定のまま**位置を1段ずらす**だけなら、段は依然一意に決まるので
  探索の重さは変わらない。しかし回路の各レベルが当たる「段幅」と「候補表」が別物になるため、
  同じ回路が別の組合せ問題になり、載らなかったものが載る可能性がある。

  例: medium(D=20) に回路段数10の threediff を置く場合
      OFFSET=0 → 段10..19 を使う（段幅 385,353,370,318,208,122,69,40,20,12）
      OFFSET=1 → 段 9..18 を使う（段幅 388,385,353,370,318,208,122,69,40,20）
      全段が1つ広い側へずれ、最終段は幅12→20になる。

物理的な前提（重要）:
  R=0 のセル（FFのD入力）は段 D-1-OFFSET に置かれるので、**その段にFFが必要**。
  構造は既定で最下段のみにFFを持つ（gen_cone_ext.py の NFFSTAGES、既定1）ので、
  OFFSET>=1 を実機として正当化するには NFFSTAGES>=OFFSET+1 で生成した構造が必要。
  （可否の探索目的なら OFFSET だけ動かして傾向を見ることはできる。その場合は物理的正当性が無いことを明記すること。）

使い方: python3 place_fixed_off.py <EBLIF> <CONE_V> [HOME_EBLIF]
環境: ATIME(秒, 既定3600) CAND_RULE(既定now) OFFSET(既定0)
"""
import sys, math, os, re, json
from collections import defaultdict
from ortools.sat.python import cp_model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load, gen_pattern
from cand_rules import make_cand

EB, GRIDV = sys.argv[1], sys.argv[2]
HOME = sys.argv[3] if len(sys.argv) > 3 else None
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
OFFSET = int(os.environ.get("OFFSET", "0"))
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D


def pis_of(eblif):
    for l in open(eblif):
        if l.startswith('.inputs'):
            return set(l.split()[1:])
    return set()


def comb_po_cells(eb, cbo):
    """組合せPO(出力のうちDFF Qでない)を出力するcboセル。FF段へ置く対象。"""
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
    cl = {o: (D - 1 - OFFSET) - RR[o] for o in cb}
    dem = defaultdict(int)
    for c in lg:
        u = c['o']
        if u not in cl: continue
        for s in c['srcs']:
            if s in cb:
                g = cl[u] - cl[s]
                if g >= 2: dem[(cl[u], g)] += 1
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
FFCOL = D - 1 - OFFSET                      # R=0 のセルが置かれる段（= FF が必要な段）
if FFCOL < 0 or maxR + 1 + OFFSET > D:
    print(f"結果: INFEASIBLE(段不足) 構造D={D} OFFSET={OFFSET} では回路FF距離段{maxR+1}が入らない"); sys.exit()
col_of = {o: FFCOL - R[o] for o in cbo}
for o in comb_po_cells(EB, cbo):            # 組合せPOを FF段へ
    col_of[o] = FFCOL
bycol = defaultdict(list)
for o in cbo:
    bycol[col_of[o]].append(o)
print(f"{CKT}: セル{len(cbo)} / FF{nff} / D={D} / OFFSET={OFFSET} FF段={FFCOL} / 使用段={min(col_of.values())}..{max(col_of.values())} / "
      f"skip枠={BUDSRC} / next_ext={next_ext}", flush=True)
for col, cs in bycol.items():
    if len(cs) > widths[col]:
        print(f"結果: INFEASIBLE(容量) 段{col}: {len(cs)} > 幅{widths[col]}"); sys.exit()

# ---- 外部入力(EXT)枠チェック(静的) ----
pi_at = defaultdict(set)
for c in logic:
    u = c['o']
    if u not in col_of: continue
    for s in c['srcs']:
        if s in PI: pi_at[col_of[u]].add(s)
ext_over = [(c, len(p), next_ext[c]) for c, p in pi_at.items() if c >= 1 and len(p) > next_ext[c]]
if ext_over:
    print(f"結果: INFEASIBLE(外部入力枠不足) 超過(段,相異なるPI需要,枠)={ext_over}"); sys.exit()

# ---- skip需要(静的) ----
skipdemand = defaultdict(int); edges1 = []; nskip = 0
for c in logic:
    u = c['o']
    if u not in col_of: continue
    for s in c['srcs']:
        if s in cbo:
            g = col_of[u] - col_of[s]
            if g == 1: edges1.append((s, u))
            elif g >= 2:
                nskip += 1; skipdemand[(col_of[u], g)] += 1
over = [(k, d, n, skipbudget.get((k, d), 0)) for (k, d), n in skipdemand.items()
        if n > skipbudget.get((k, d), 0)]
if over:
    print(f"結果: INFEASIBLE(skip枠不足) 超過(段,距離,需要,枠)={over}  skip総数={nskip}"); sys.exit()

CAND_RULE = os.environ.get("CAND_RULE", "now")
cand = {col: make_cand(widths[col - 1], widths[col], CAND_RULE, row=col) for col in range(1, D)}
_sel = lambda n: max(1, math.ceil(math.log2(n))) if n > 1 else 0
_now = {col: gen_pattern(widths[col - 1], widths[col]) for col in range(1, D)}
print(f"候補規則 CAND_RULE={CAND_RULE}: 候補 {sum(len(x) for c in cand for x in cand[c])} 本 (now {sum(len(x) for c in _now for x in _now[c])})"
      f"  段間imux選択bitの目安 {sum(2*_sel(len(x)) for c in cand for x in cand[c])} (now {sum(2*_sel(len(x)) for c in _now for x in _now[c])})", flush=True)
m = cp_model.CpModel()
row = {o: m.NewIntVar(0, widths[col_of[o]] - 1, '') for o in cbo}
for col, cs in bycol.items():
    if len(cs) > 1:
        m.AddAllDifferent([row[o] for o in cs])
pairs = {}
for cu in range(1, D):
    pairs[cu] = [(rp, r) for r in range(widths[cu]) for rp in cand[cu][r]]
for s, u in edges1:
    m.AddAllowedAssignments([row[s], row[u]], pairs[col_of[u]])

sv = cp_model.CpSolver()
sv.parameters.max_time_in_seconds = int(os.environ.get("ATIME", "3600"))
sv.parameters.num_search_workers = 8
st = sv.Solve(m)
print(f"結果: {sv.StatusName(st)} ({sv.WallTime():.0f}s)  gap1={len(edges1)} skip={nskip}"
      f"  外部入力需要(段:相異PI)={ {c: len(p) for c, p in sorted(pi_at.items())} }", flush=True)
if sv.StatusName(st) in ('FEASIBLE', 'OPTIMAL'):
    json.dump({'col': col_of, 'row': {o: sv.Value(row[o]) for o in cbo}, 'OFFSET': OFFSET},
              open(f'place_fixed_off_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_fixed_off_{CKT}.json")
