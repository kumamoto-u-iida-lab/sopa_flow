#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_ft_cone.py — フィードスルー(中継)を「配置配線の中で」決めるcone配置(CP-SAT)。
   place_skip_cone.py は壊さず別ファイルにしてある(既存結果の再現性のため)。

【place_skip_cone.py との違い = 案A】
 ① 中継(フィードスルー): ネットリストに手を加えず、空きスロットを中継に転用できる。
    PAは B側に定数1 / MODE=2'b00 で O=A の素通しになる(追加config 0bit、実測確認済 8/23)。
    → 従来は中継セルを事前にネットリストへ書き込んでいた(sortmax: 4個挿入したが必要は1個)。
 ② skipの相乗り: 1本のskipトラックの出力は着地段の【全imux】に配られる(Verilog実測)。
    よって同じ(信号,着地段,gap)なら何個のPAが読んでもトラックは1本。
    → 従来は辺ごとに1本と数えていた(sortmaxで6本ぶん過剰カウント)。
 ③ 中継数を最小化する目的関数(env MINREL=0 で無効)。

【モデル】
  body[o][k]     セルoの本体が段kに居る
  relay[o][k]    信号σ_o の中継が段kに居る
  atrow[o][k][r] σ_o が段k・行r の出力として存在する(本体でも中継でもよい)
  trk[o][k][d]   (段k, gap d) のトラック1本を σ_o に割り当てる
【制約】
  (1) 生成 各oはちょうど1段に本体   (2) 伝播 relay は 段k-1から隣接 or トラックで受ける
  (3) 消費 段Kのセルuがσ_sを読む    (4) 容量 (段,行)に高々1つ / トラック数 <= 構造の持ち分
使い方: python3 place_ft_cone.py <EBLIF> <CONE_V>
環境: ATIME(秒,既定300) FFLAST=1(mustを最下段固定) MINREL=0(中継最小化を切る)
"""
import sys, os, re, json
from collections import defaultdict
from ortools.sat.python import cp_model

CONST = {'$true', '$false', '$undef'}
EBLIF, GRIDV = sys.argv[1], sys.argv[2]
CKT = os.path.basename(EBLIF).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
ATIME = float(os.environ.get('ATIME', 300))
MINREL = os.environ.get('MINREL', '1') != '0'

# ---------- eblif ----------
cells, dffs, pos = [], [], []
for l in open(EBLIF):
    t = l.strip()
    if t.startswith('.outputs'): pos = t.split()[1:]
    elif t.startswith('.subckt cell'):
        p = dict(x.split('=', 1) for x in t.split()[2:])
        cells.append({'o': p['O_a'], 'srcs': [s for s in (p.get('I_a'), p.get('I_b')) if s and s not in CONST]})
    elif t.startswith('.subckt DFF'): dffs.append(dict(x.split('=', 1) for x in t.split()[2:]))
cr = {d['C'] for d in dffs} | {d['R'] for d in dffs}
logic = [c for c in cells if c['o'] not in cr]
dq = {d['Q'] for d in dffs}; cbo = {c['o']: c for c in logic}
cpo = [p for p in pos if p not in dq]
# ★2026-08-31 変更: 組合せPOは【複製せず移動】する。
#   構造の最下段には FLIPFLOP_NODE (2to1MUX: 通す/登録) が付いていて、その出力は
#   pa_o(外部出力) と FFfb(全段の全IMUXの候補) の両方へ出る（girl10.v の実物で確認済み）。
#   よって POセル自身を最下段に置けば、外部出力にも内部の読み手にも同時に届き、
#   後ろ向きの辺にならない。→ 複製は不要（2026-08-04 の結論どおり）。
#   複製していた版は要らないセルを1個作り、構造の総スロットを1個超えて
#   INFEASIBLE になっていた（2026-08-30 に41回路で確認: セル数 = 総スロット + 1）。
must = {d['D'] for d in dffs if d['D'] in cbo} | {p for p in cpo if p in cbo}

# ---------- cone構造 ----------
g = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', g).group(1).split(',')]
D = len(widths); WMAX = max(widths)
# ★2026-08-31 追加: FFfb（FF段出力の全段ブロードキャスト）をモデルに入れる。
#   構造の実物(girl10.v で確認): 最下段の全PA出力は FLIPFLOP_NODE(2to1MUX: 通す/登録)を
#   通って o_c<段>_<行> になり、それが【全段の全IMUX】の候補に入っている。
#     IMUX_IN015 imux_c1_0_ia (.IMUX_I_0(o_c6_0), .IMUX_I_1(o_c6_1), ... )
#   このモデルはこれまで前向きの辺しか持っておらず、FF段に置いた信号を
#   前の段が読めなかった。そのため組合せPOを「複製」して回避していた。
#   FLIPFLOP_NODE が実際に付いている段を .v から読む（NFFSTAGES>1 にも追随する）。
FFB_STAGES = sorted({int(x) for x in re.findall(r'FLIPFLOP_NODE\s+ff_c(\d+)_\d+', g)})
FF_START = (D - 1) if os.environ.get('FFLAST') else max(1, D - 3)
cand = defaultdict(dict)
for mm in re.finditer(r'//\s*行(\d+)\s*PA(\d+):\s*候補\(前行\)=\s*\[([0-9,\s]*)\]', g):
    cand[int(mm.group(1))][int(mm.group(2))] = [int(x) for x in mm.group(3).split(',')]
bud = defaultdict(int)
for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段', g):
    bud[(int(mm.group(2)), int(mm.group(3)))] += 1
GAPS = defaultdict(list)                       # 段k で使える gap の一覧
for (k, d), n in bud.items():
    if n > 0: GAPS[k].append(d)

# ---------- ASAP / ALAP ----------
ASAP = {}; rem = list(logic)
while rem:
    nx = []
    for c in rem:
        ss = [s for s in c['srcs'] if s in cbo]
        if all(s in ASAP for s in ss): ASAP[c['o']] = max([ASAP[s] + 1 for s in ss] + [0])
        else: nx.append(c)
    if len(nx) == len(rem): break
    rem = nx
dist = {o: 0 for o in must}; ch = True
while ch:
    ch = False
    for c in logic:
        nd = dist.get(c['o'])
        if nd is None: continue
        for s in c['srcs']:
            if s in cbo and dist.get(s, -1) < nd + 1: dist[s] = nd + 1; ch = True
LO = {o: (D - 1 if o in must else min(ASAP.get(o, 0), D - 1)) for o in cbo}
HI = {o: (D - 1 if o in must else D - 1 - dist.get(o, 0)) for o in cbo}
for o in cbo:
    if o in must: LO[o] = max(FF_START, LO[o])
    if LO[o] > HI[o]:
        print(f"結果: INFEASIBLE (段の範囲が空: {o})"); sys.exit(0)

consumers = defaultdict(list)
for c in logic:
    for s in c['srcs']:
        if s in cbo: consumers[s].append(c['o'])
# σ_o が居られる段の窓: 本体 [LO,HI] ∪ 中継 (LO, 消費者の最遅段-1]
WIN = {}
for o in cbo:
    # 上端は「消費者の最遅段」まで。−1にすると、その段へ skip で飛ぶ trk が作られない。
    hi = HI[o]
    if consumers[o]: hi = max(hi, max(HI[u] for u in consumers[o]))
    WIN[o] = (LO[o], min(hi, D - 1))

print(f"{CKT}: セル{len(cbo)} / must{len(must)} / D={D} widths={widths} / "
      f"skipトラック{sum(bud.values())}本 / 総スロット{sum(widths)}", flush=True)
ff_slots = sum(widths[k] for k in range(FF_START, D))
if len(must) > ff_slots:
    print(f"結果: INFEASIBLE (must{len(must)} > FF枠{ff_slots})"); sys.exit(0)

# ---------- CP-SAT ----------
m = cp_model.CpModel()
body, relay, atrow, outv, trk = {}, {}, {}, {}, {}
for o in cbo:
    lo, hi = WIN[o]
    for k in range(lo, hi + 1):
        if LO[o] <= k <= HI[o]: body[o, k] = m.NewBoolVar(f'b_{o}_{k}')
        if k > LO[o]:           relay[o, k] = m.NewBoolVar(f'r_{o}_{k}')
    m.AddExactlyOne([body[o, k] for k in range(LO[o], HI[o] + 1)])          # (1) 生成
    for k in range(lo, hi + 1):
        bb = body.get((o, k)); rr = relay.get((o, k))
        ov = m.NewBoolVar(f'o_{o}_{k}'); outv[o, k] = ov
        srcs = [x for x in (bb, rr) if x is not None]
        m.AddAtMostOne(srcs)                                     # 同じ段に本体と中継は置かない
        m.AddMaxEquality(ov, srcs)
        rowvars = []
        for r in range(widths[k]):
            a = m.NewBoolVar(f'a_{o}_{k}_{r}'); atrow[o, k, r] = a; rowvars.append(a)
            m.AddImplication(a, ov)
        m.Add(sum(rowvars) == 1).OnlyEnforceIf(ov)
        m.Add(sum(rowvars) == 0).OnlyEnforceIf(ov.Not())
        for d in GAPS.get(k, []):
            if lo <= k - d:
                t = m.NewBoolVar(f't_{o}_{k}_{d}'); trk[o, k, d] = t
                m.AddImplication(t, outv[o, k - d])               # トラックの元が段k-dに居ること
                # ※トラックで届くことは受け取り側(receive_clause)の選択肢として表現する。
                #   ここで outv[o,k] を強制すると「skipを使うたびに中継が要る」ことになり誤り。

# (4) 容量: 各(段,行)に高々1つ
occ = defaultdict(list)
for (o, k, r), a in atrow.items(): occ[k, r].append(a)
for kr, lst in occ.items():
    if len(lst) > 1: m.AddAtMostOne(lst)
# (4) トラック本数
tk = defaultdict(list)
for (o, k, d), t in trk.items(): tk[k, d].append(t)
for (k, d), lst in tk.items(): m.Add(sum(lst) <= bud[(k, d)])

# ★FFfb で全段へ配ってよい信号
#   条件: FF段に固定される must であって、【他の論理セルを入力に持たない】もの。
#   入辺が無ければ、その信号を全段へ配っても組合せループは作れない。
#   全41回路で組合せPO(pr_state[0]等)がこれに該当する
#   （入力は DFF-Q か外部入力のみ＝2026-08-31 に41回路で確認）。
#   DFF-D駆動セルは入辺を持つので対象外（そもそもFFfbで読む必要がない。
#   その先はDFFであり、DFFのQは cbo の外にある別信号として扱われる）。
FFB_OK = {o for o in must if not [x for x in cbo[o]['srcs'] if x in cbo]}
_skip = sorted(o for o in must if o not in FFB_OK)
print(f"  FFfb対象 {len(FFB_OK)}信号 / FF段 {FFB_STAGES} "
      f"(入辺ありのため対象外 {len(_skip)}信号)", flush=True)


def receive_clause(sig, k, r, gate):
    """信号sig を 段k・行r の受け手が取れる条件。gate が真ならこの節を強制。"""
    lits = []
    for rp in cand.get(k, {}).get(r, []):
        a = atrow.get((sig, k - 1, rp))
        if a is not None: lits.append(a)
    for d in GAPS.get(k, []):
        t = trk.get((sig, k, d))
        if t is not None: lits.append(t)
    # ★FFfb: sig が FF段に居るなら、どの段のどの行からでも読める（行に依らない全結線）
    if sig in FFB_OK:
        for kf in FFB_STAGES:
            ov = outv.get((sig, kf))
            if ov is not None and kf != k - 1: lits.append(ov)
    if lits: m.AddBoolOr(lits).OnlyEnforceIf(gate)
    else:    m.Add(gate == 0)

# (2) 伝播: 中継が段k・行rに居るなら、σ_o を受け取れること
for (o, k), rr in relay.items():
    for r in range(widths[k]):
        gate = m.NewBoolVar('')
        m.AddBoolAnd([rr, atrow[o, k, r]]).OnlyEnforceIf(gate)
        m.AddBoolOr([rr.Not(), atrow[o, k, r].Not()]).OnlyEnforceIf(gate.Not())
        receive_clause(o, k, r, gate)
# (3) 消費: 段K・行r に居る本体 u が、入力 s を取れること
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s not in cbo: continue
        for K in range(LO[u], HI[u] + 1):
            bb = body.get((u, K))
            if bb is None or K == 0: continue
            for r in range(widths[K]):
                gate = m.NewBoolVar('')
                m.AddBoolAnd([bb, atrow[u, K, r]]).OnlyEnforceIf(gate)
                m.AddBoolOr([bb.Not(), atrow[u, K, r].Not()]).OnlyEnforceIf(gate.Not())
                receive_clause(s, K, r, gate)

if MINREL: m.Minimize(sum(relay.values()))

sol = cp_model.CpSolver()
sol.parameters.max_time_in_seconds = ATIME
sol.parameters.num_search_workers = int(os.environ.get('WORKERS', 8))
sol.parameters.log_search_progress = False
st = sol.Solve(m)
name = sol.StatusName(st)
print(f"結果: {name} ({sol.WallTime():.0f}s)", flush=True)
if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): sys.exit(0)

col = {o: k for (o, k), b in body.items() if sol.Value(b)}
rel = [(o, k) for (o, k), r in relay.items() if sol.Value(r)]
row = {}
for (o, k, r), a in atrow.items():
    if sol.Value(a) and (col.get(o) == k or (o, k) in rel): row[o, k] = r
usedtrk = defaultdict(int)
for (o, k, d), t in trk.items():
    if sol.Value(t): usedtrk[(k, d)] += 1
occk = defaultdict(int)
for o, k in col.items(): occk[k] += 1
relk = defaultdict(int)
for o, k in rel: relk[k] += 1
print(f"  ★中継(フィードスルー) = {len(rel)}個" + (f"  段別: {dict(sorted(relk.items()))}" if rel else ""))
print(f"  本体の段分布: {[occk.get(k,0) for k in range(D)]}")
print(f"  中継こみ占有: {[occk.get(k,0)+relk.get(k,0) for k in range(D)]} / 段幅 {widths}")
byd = defaultdict(int)
for (k, d), n in usedtrk.items(): byd[d] += n
print(f"  skipトラック使用 = {sum(usedtrk.values())}本  距離別: {dict(sorted(byd.items()))} / 構造の持ち分 {sum(bud.values())}本")
# ★2026-08-31: 下流(gen_config_verilog.py)は row を「セル名 -> 行」で読む。
#   このツールは中継のぶん (セル,段) をキーにしているので、本体の行だけを取り出した
#   旧 place_skip_cone.py 互換のキーも一緒に書く。中継が0個なら両者は完全に等価。
#   row_body … 本体の行だけ（旧形式）  row … 中継こみ（このツール独自）
row_body = {o: row[(o, k)] for o, k in col.items() if (o, k) in row}
out = {'col': col, 'row': row_body,
       'relay': [[o, k] for o, k in rel],
       'row_all': {f'{o}@{k}': r for (o, k), r in row.items()},
       'trk': {f'{k},{d}': n for (k, d), n in usedtrk.items()}}
fn = f'place_ft_cone_{CKT}.json'
json.dump(out, open(fn, 'w'), ensure_ascii=False)
print(f"  保存: {fn}")
