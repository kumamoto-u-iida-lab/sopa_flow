#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_free_tbl.py — 段(col)も行(row)も CP-SAT で解く「全体SAT」版。2026-09-26。

由来: /home/iidalab/Kohata/SoPA-main/src/place_skip_cone.py（2026-08-03 版）を元に、
      place_fixed_tbl.py（段固定・表制約版）と**同じ土俵で比較できる**ように作り直したもの。
      元ファイルは一切変更していない（このリポジトリの慣行どおり複製して別名）。

place_skip_cone.py から直した点（重要）:
 ① **__po_copy__ の廃止**。元版は組合せPOのセルを複製し、その複製を下3段に強制していた。
    複製は元と同じ入力源を読むため gap==1 と併せて「元セルと複製が同じ段」を強いられ、
    錐体全体が最終段側へ押し込まれて偽の INFEASIBLE になっていた（indep/cat/girl10 で確認）。
    → place_fixed_tbl.py と同じく「組合せPOのセル自体を最下段へ固定」に変更（.conn 別名解決も移植）。
 ② **セル解析を place_greedy.load() に統一**。元版は独自パースでセル数が1個ずれていた(171 vs 170)。
 ③ **外部入力(EXT)の段別枠に対応**。元版は N_EXT_LIST を読まず、PI を入力源として数えていなかった。
    段が変数なので静的判定は使えない → PI ごとに「段kで使う」Boolを立て、
    段ごとの相異なるPI数 <= next_ext[k] を論理制約で課す（段0は直受けなので対象外）。
 ④ **符号化を表制約に**。元版は辺×段×幅×候補数の Bool を量産し、col==k の Bool も辺ごとに作り直していた。
    → AddAllowedAssignments([col[u], row[s], row[u]], 許可3つ組) 1個／辺。col==k の Bool は (セル,段) で1回だけ。
 ⑤ **重複配置の禁止を AddAllDifferent 1個に**。元版はセル対ごとの比較で O(n^2) の Bool を作っていた。
    → slot = col*WMAX + row の AllDifferent。

解いている問題:
 - col[o] は [ASAP, ALAP] の範囲で自由（skip 枠のある構造では段を選ぶ自由度が実際に生まれる）
 - 辺は gap=1（隣接候補表に従う）または gap>=2（skip 枠の範囲で行自由）
 - 各段の本体数 <= widths[段]、同一(段,行)は1セルまで
 - must（FFのD入力・組合せPO）は既定で最下段 D-1 に固定（FFSPAN=n で下n段に緩める）

注意: skip を持たない中継挿入済み構造では MAXSKIP=1 となり全辺が gap==1 に固定されるため、
      must を最下段に固定すると col は一意に決まる（= place_fixed_tbl.py と同じ配置）。
      段の自由度が意味を持つのは skip 配線を持つ構造か、中継未挿入のネットリストの場合。

使い方: python3 place_free_tbl.py <EBLIF> <CONE_V> [HOME_EBLIF]
環境:
  ATIME     秒（既定3600）
  CAND_RULE 指定すると cand_rules.make_cand で候補表を作る（既定: 構造 .v の埋め込みコメントを使う）
  FFSPAN    must を下n段に許容（既定1＝最下段のみ）
"""
import sys, os, re, json, math
from collections import defaultdict
from ortools.sat.python import cp_model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load

EB, GRIDV = sys.argv[1], sys.argv[2]
HOME = sys.argv[3] if len(sys.argv) > 3 else None
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths); WMAX = max(widths)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D
FFSPAN = max(1, int(os.environ.get("FFSPAN", "1")))
FF_START = max(1, D - FFSPAN)


def pis_of(eblif):
    for l in open(eblif):
        if l.startswith('.inputs'):
            return set(l.split()[1:])
    return set()


def comb_po_cells(eb, cbo):
    """組合せPO(出力のうちDFF Qでない)を出力するcboセル。最下段(FF段)へ置く対象。
       place_fixed_tbl.py から移植（.conn の別名を遡って解決する）。"""
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
        if u not in cl: continue
        for s in c['srcs']:
            if s in cb:
                g = cl[u] - cl[s]
                if g >= 2: dem[(cl[u], g)] += 1
    return dem


# ---------- skip 枠 ----------
if HOME:
    skipbudget = skip_demand(HOME)
    BUDSRC = f"home={os.path.basename(HOME)}の実需要"
else:
    skipbudget = defaultdict(int)
    for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段', gtxt):
        skipbudget[(int(mm.group(2)), int(mm.group(3)))] += 1
    BUDSRC = ".v定義枠"
MAXSKIP = max([d for (_, d) in skipbudget], default=1)

# ---------- 回路 ----------
PI = pis_of(EB)
logic, cbo, R, nff = load(EB)
maxR = max(R.values())
if maxR + 1 > D:
    print(f"結果: INFEASIBLE(段不足) 構造D={D} < 回路FF距離段{maxR+1}"); sys.exit()
po_moved = set(comb_po_cells(EB, cbo))   # 組合せPOのセル: 最下段へ引き上げる
must = set(po_moved)
must |= {o for o in cbo if R[o] == 0}   # FFのD入力など R=0 のセルは最下段側

# ---------- 候補表 ----------
CAND_RULE = os.environ.get("CAND_RULE")
if CAND_RULE:
    from cand_rules import make_cand
    cand = {k: make_cand(widths[k - 1], widths[k], CAND_RULE, row=k) for k in range(1, D)}
    CSRC = f"cand_rules(CAND_RULE={CAND_RULE})"
else:
    _c = defaultdict(dict)
    for mm in re.finditer(r'//\s*行(\d+)\s*PA(\d+):\s*候補\(前行\)=\s*\[([0-9,\s]*)\]', gtxt):
        v = [int(x) for x in mm.group(3).split(',') if x.strip() != '']
        _c[int(mm.group(1))][int(mm.group(2))] = v
    cand = {k: [_c[k].get(r, []) for r in range(widths[k])] for k in range(1, D)}
    CSRC = ".v埋め込み候補表"
ncand = sum(len(x) for k in cand for x in cand[k])

print(f"{CKT}: セル{len(cbo)} / FF{nff} / D={D} / must{len(must)} / skip枠={BUDSRC} MAXSKIP={MAXSKIP} / "
      f"候補={CSRC} {ncand}本 / next_ext={next_ext}", flush=True)

# ---------- ASAP / ALAP ----------
ASAP = {}; rem = list(logic)
while rem:
    nx = []
    for c in rem:
        ss = [s for s in c['srcs'] if s in cbo]
        if all(s in ASAP for s in ss):
            ASAP[c['o']] = max([ASAP[s] + 1 for s in ss] + [0])
        else:
            nx.append(c)
    if len(nx) == len(rem):
        for c in nx: ASAP[c['o']] = 0          # 循環（FF帰還など）は0扱い
        break
    rem = nx
dist = {o: 0 for o in must}
ch = True
while ch:
    ch = False
    for c in logic:
        nd = dist.get(c['o'])
        if nd is None: continue
        for s in c['srcs']:
            if s in cbo and dist.get(s, -1) < nd + 1:
                dist[s] = nd + 1; ch = True
lo = {o: min(ASAP.get(o, 0), D - 1) for o in cbo}
hi = {o: (D - 1) - dist.get(o, 0) for o in cbo}
for o in must: hi[o] = D - 1
bad = [(o, lo[o], hi[o]) for o in cbo if lo[o] > hi[o]]
if bad:
    print(f"結果: INFEASIBLE(段範囲矛盾) 例={bad[:3]} 件数={len(bad)}"); sys.exit()

# ---------- CP-SAT ----------
m = cp_model.CpModel()
col = {o: m.NewIntVar(lo[o], hi[o], '') for o in cbo}
row = {o: m.NewIntVar(0, WMAX - 1, '') for o in cbo}
for o in must:
    m.Add(col[o] >= FF_START)

# (セル,段) の channeling Bool を1回だけ作る
at = {}
for o in cbo:
    vs = {}
    for k in range(lo[o], hi[o] + 1):
        b = m.NewBoolVar('')
        m.Add(col[o] == k).OnlyEnforceIf(b)
        m.Add(col[o] != k).OnlyEnforceIf(b.Not())
        m.Add(row[o] < widths[k]).OnlyEnforceIf(b)
        vs[k] = b
    m.AddExactlyOne(vs.values())
    at[o] = vs

# 同一(段,行)は1セルまで
slots = []
for o in cbo:
    s = m.NewIntVar(0, D * WMAX - 1, '')
    m.Add(s == col[o] * WMAX + row[o])
    slots.append(s)
m.AddAllDifferent(slots)

# 段容量
for k in range(D):
    bs = [at[o][k] for o in cbo if k in at[o]]
    if bs and len(bs) > widths[k]:
        m.Add(sum(bs) <= widths[k])

# 辺: gap=1 は表制約 / gap>=2 は skip 枠
tbl = [(k, rp, r) for k in range(1, D) for r in range(widths[k]) for rp in cand[k][r]]
skip_use = defaultdict(list)
n_e = 0
for c in logic:
    u = c['o']
    if u not in cbo: continue
    for s in c['srcs']:
        if s not in cbo: continue
        # ★組合せPOセルを起点とする辺は数えない。place_fixed_tbl.py は組合せPOを最下段へ移した結果
        #   生じる後ろ向き辺(g<=0)を「FFfbが吸収」として黙って捨てている。同じ扱いに揃える。
        #   これを課すと col[u]==col[s]+1 が段18を要求して即矛盾する（0秒 INFEASIBLE の原因だった）。
        if s in po_moved: continue
        n_e += 1
        if MAXSKIP == 1:
            m.Add(col[u] == col[s] + 1)
            m.AddAllowedAssignments([col[u], row[s], row[u]], tbl)
        else:
            g = m.NewIntVar(1, MAXSKIP, '')
            m.Add(g == col[u] - col[s])
            is1 = m.NewBoolVar('')
            m.Add(g == 1).OnlyEnforceIf(is1)
            m.Add(g != 1).OnlyEnforceIf(is1.Not())
            # gap=1 のときだけ表制約を効かせる（表制約は enforcement 不可なので col を含めた表で表現）
            t1 = [(k, rp, r) for (k, rp, r) in tbl]
            cu2 = m.NewIntVar(0, D - 1, ''); m.Add(cu2 == col[u]).OnlyEnforceIf(is1)
            m.Add(cu2 == 0).OnlyEnforceIf(is1.Not())
            rs2 = m.NewIntVar(0, WMAX - 1, ''); m.Add(rs2 == row[s]).OnlyEnforceIf(is1)
            ru2 = m.NewIntVar(0, WMAX - 1, ''); m.Add(ru2 == row[u]).OnlyEnforceIf(is1)
            m.AddAllowedAssignments([cu2, rs2, ru2], t1 + [(0, x, y) for x in range(WMAX) for y in range(WMAX)])
            for d in range(2, MAXSKIP + 1):
                isd = m.NewBoolVar('')
                m.Add(g == d).OnlyEnforceIf(isd)
                m.Add(g != d).OnlyEnforceIf(isd.Not())
                for k in range(d, D):
                    if k not in at[u]: continue
                    use = m.NewBoolVar('')
                    m.AddBoolAnd([isd, at[u][k]]).OnlyEnforceIf(use)
                    m.AddBoolOr([isd.Not(), at[u][k].Not()]).OnlyEnforceIf(use.Not())
                    skip_use[(k, d)].append(use)
for (k, d), uses in skip_use.items():
    m.Add(sum(uses) <= skipbudget.get((k, d), 0))

# 外部入力(EXT)の段別枠: 段k(1..D-1) の相異なるPI数 <= next_ext[k]
readers = defaultdict(set)
for c in logic:
    u = c['o']
    if u not in cbo: continue
    for s in c['srcs']:
        if s in PI: readers[s].add(u)
for k in range(1, D):
    uses = []
    for p, us in readers.items():
        bs = [at[u][k] for u in us if k in at[u]]
        if not bs: continue
        pu = m.NewBoolVar('')
        for b in bs: m.AddImplication(b, pu)
        uses.append(pu)
    if uses:
        m.Add(sum(uses) <= next_ext[k])

sv = cp_model.CpSolver()
sv.parameters.max_time_in_seconds = int(os.environ.get("ATIME", "3600"))
sv.parameters.num_search_workers = 8
st = sv.Solve(m)
name = sv.StatusName(st)
if name in ('FEASIBLE', 'OPTIMAL'):
    cv = {o: sv.Value(col[o]) for o in cbo}
    g1 = ns = 0
    for c in logic:
        u = c['o']
        if u not in cv: continue
        for s in c['srcs']:
            if s in cv:
                g = cv[u] - cv[s]
                if g == 1: g1 += 1
                elif g >= 2: ns += 1
    pi_at = defaultdict(set)
    for c in logic:
        u = c['o']
        if u not in cv: continue
        for s in c['srcs']:
            if s in PI: pi_at[cv[u]].add(s)
    print(f"結果: {name} ({sv.WallTime():.0f}s)  gap1={g1} skip={ns}"
          f"  外部入力需要(段:相異PI)={ {c: len(p) for c, p in sorted(pi_at.items())} }", flush=True)
    w = defaultdict(int)
    for o in cbo: w[cv[o]] += 1
    print(f"  本体の段分布(0->D-1): {[w[k] for k in range(D)]} / 段幅: {widths}", flush=True)
    json.dump({'col': cv, 'row': {o: sv.Value(row[o]) for o in cbo}},
              open(f'place_free_tbl_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_free_tbl_{CKT}.json", flush=True)
else:
    print(f"結果: {name} ({sv.WallTime():.0f}s)  gap1=- skip=-", flush=True)
