#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""place_sa_fixed.py — 段固定の行割り当てを【焼きなまし(SA)】で解く軽量配置配線。

2026-09-02 作成。IPGen 側の SA ツール
  pae-efpga-tools-BSGen_patopae/src/BitstreamGen/SAPR/SimulatedAnnealingSparse_FF1.py
の phase1（初期配置 → 入替え → 配線可否ペナルティ → シグモイド冷却）の骨組みを、
SoPA の段固定問題に移植したもの。place_fixed_skip_ext.py（CP-SAT 版）と同じ入出力。

■ 解く問題（place_fixed_skip_ext.py と同一）
  段     col = D-1-R（R = FFまでの最長距離）に固定。組合せPOは最下段へ移動。
  行     各段で 1行1セル。
  制約   隣接辺 (s→u, gap1) ごとに  row[s] ∈ cand[col_u][row[u]]
         （u の imux が前段の s を選べる行か。cand は幅から gen_pattern で決まる）
  skip辺(gap≥2) はトラックの本数だけ静的に確認（行の制約は無い）。
  外部入力(EXT)・定数・FFfb は全 imux に入っているので行の制約は無い。

■ IPGen SA からの流用と変更
  状態   IPGen: 論理PAE→物理PAE       ここ: セル→行（段は固定）
  手     IPGen: 2つを入替え/空きへ移動  ここ: 同じ。ただし【同じ段の中だけ】
  コスト IPGen: 毎回全辺を再評価        ここ: 違反辺の本数。動かした2セルの辺だけ差分計算
  ★コスト（第2版 2026-09-02）: 違反の「本数」でなく【許可ブロックまでの距離】。
         cand は A_k = min(N, 2N/k) の被覆則で、前段の行 k を読める段c の行は連続した
         2N/k 本のブロック。行0,1,2 は全行から読める「万能行」、行番号が大きいほど読み手は少ない。
         本数コストは「近づいても 0 のまま」で勾配が無く収束しなかった（第1版の教訓）。
  手     最小衝突法: 違反辺の端点を1つ選び、同じ段の全行を評価して一番コストが下がる行へ入替え。
         ときどき(PNOISE)ランダム行。悪化する手は温度 T で確率的に受理。
  初期   各段でファンアウト（次段への辺数）の多いセルから行0,1,2… に置く（万能行を大ファンアウトに）
  終了   cost==0 で FEASIBLE。時間内に 0 にならなければ再スタート（乱数を変えて）

■ 結果の読み方
  FEASIBLE  = 載る（解を1つ見つけた。CP-SAT 版の OPTIMAL と同じ意味）
  UNKNOWN   = 時間内に見つからなかった。【載らない証明ではない】（SAの限界）
  INFEASIBLE(...) = 静的チェック（容量/EXT枠/skip枠）で不可と分かった場合のみ

 使い方: python3 place_sa_fixed.py <EBLIF> <CONE_V>
 環境変数: ATIME(秒, 既定120) / ITERS(1回の反復上限, 既定 200,000) / SEED / T0(既定0.3) / PNOISE(ランダム手の割合, 既定0.1)
 出力: place_sa_fixed_<回路>.json  {'col':..., 'row':...}（gen_config_verilog.py がそのまま読める）
"""
import sys, os, re, json, math, random, time
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load, gen_pattern

EB, GRIDV = sys.argv[1], sys.argv[2]
CKT = os.path.basename(EB).replace('mapped_', '').replace('.v.eblif', '').replace('.eblif', '')
ATIME = float(os.environ.get("ATIME", "120"))
ITERS = int(os.environ.get("ITERS", "200000"))
T0 = float(os.environ.get("T0", "0.3"))
PNOISE = float(os.environ.get("PNOISE", "0.1"))
SEED = int(os.environ.get("SEED", "1"))

gtxt = open(GRIDV).read()
widths = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', gtxt).group(1).split(',')]
D = len(widths)
m_ne = re.search(r'N_EXT_LIST=\[([0-9,\s]*)\]', gtxt)
next_ext = [int(x) for x in m_ne.group(1).split(',')] if m_ne else [0] * D
skipbudget = defaultdict(int)
for mm in re.finditer(r'//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段', gtxt):
    skipbudget[(int(mm.group(2)), int(mm.group(3)))] += 1


def pis_of(eblif):
    for l in open(eblif):
        if l.startswith('.inputs'):
            return set(l.split()[1:])
    return set()


def comb_po_cells(eb, cbo):
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


# ---------- 段固定・静的チェック（place_fixed_skip_ext.py と同じ） ----------
PI = pis_of(EB)
logic, cbo, R, nff = load(EB)
maxR = max(R.values())
if maxR + 1 > D:
    print(f"結果: INFEASIBLE(段不足) 構造D={D} < 回路FF距離段{maxR+1}"); sys.exit()
col_of = {o: (D - 1) - R[o] for o in cbo}
for o in comb_po_cells(EB, cbo):
    col_of[o] = D - 1
bycol = defaultdict(list)
for o in cbo:
    bycol[col_of[o]].append(o)
print(f"{CKT}: セル{len(cbo)} / FF{nff} / D={D} / SA(ATIME={ATIME:.0f}s ITERS={ITERS} T0={T0} PNOISE={PNOISE})", flush=True)
for col, cs in bycol.items():
    if len(cs) > widths[col]:
        print(f"結果: INFEASIBLE(容量) 段{col}: {len(cs)} > 幅{widths[col]}"); sys.exit()
pi_at = defaultdict(set)
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s in PI:
            pi_at[col_of[u]].add(s)
ext_over = [(c, len(p), next_ext[c]) for c, p in pi_at.items() if c >= 1 and len(p) > next_ext[c]]
if ext_over:
    print(f"結果: INFEASIBLE(外部入力枠不足) 超過(段,相異なるPI需要,枠)={ext_over}"); sys.exit()
skipdemand = defaultdict(int)
edges1 = []
nskip = 0
for c in logic:
    u = c['o']
    for s in c['srcs']:
        if s in cbo:
            g = col_of[u] - col_of[s]
            if g == 1:
                edges1.append((s, u))
            elif g >= 2:
                nskip += 1
                skipdemand[(col_of[u], g)] += 1
over = [(k, d, n, skipbudget.get((k, d), 0)) for (k, d), n in skipdemand.items() if n > skipbudget.get((k, d), 0)]
if over:
    print(f"結果: INFEASIBLE(skip枠不足) 超過(段,距離,需要,枠)={over}  skip総数={nskip}"); sys.exit()

# ---------- SA の下ごしらえ ----------
# allowed[c][r] = 段c 行r の imux が選べる前段の行の集合
cand = {c: gen_pattern(widths[c - 1], widths[c]) for c in range(1, D)}
allowed = {c: [set(x) for x in cand[c]] for c in cand}
# dist[c][k][r] = 段c の行r から「前段の行k を読めるブロック」までの巡回距離（0=読める）
dist = {}
for c in cand:
    n = widths[c]; ns = widths[c - 1]
    readers = [[r for r in range(n) if k in allowed[c][r]] for k in range(ns)]
    tab = []
    for k in range(ns):
        rs = readers[k]
        if not rs:
            tab.append([n] * n); continue
        row_d = []
        for r in range(n):
            row_d.append(min(min(abs(r - a), n - abs(r - a)) for a in rs))
        tab.append(row_d)
    dist[c] = tab
out_e = defaultdict(list)   # s -> [u]
in_e = defaultdict(list)    # u -> [s]
for s, u in edges1:
    out_e[s].append(u); in_e[u].append(s)

row = {}
occ = {c: [None] * widths[c] for c in range(D)}


def ecost(s, u):
    return dist[col_of[u]][row[s]][row[u]]


def cell_cost(o):
    v = 0
    for u in out_e[o]: v += dist[col_of[u]][row[o]][row[u]]
    for s in in_e[o]: v += dist[col_of[o]][row[s]][row[o]]
    return v


def total_cost():
    return sum(ecost(s, u) for s, u in edges1)


def n_viol():
    return sum(1 for s, u in edges1 if ecost(s, u) > 0)


def initial(rng):
    """各段で、次段へのファンアウトが多いセルから行0,1,2…（万能行）に置く。同点は乱数。"""
    for c in range(D):
        for r in range(widths[c]): occ[c][r] = None
        cells = list(bycol.get(c, []))
        cells.sort(key=lambda o: (-len(out_e[o]), rng.random()))
        for r, o in enumerate(cells):
            row[o] = r; occ[c][r] = o


def swap_delta(o, r2):
    """o を行 r2 へ（占有者と入替え）したときのコスト差"""
    c = col_of[o]; r1 = row[o]; p = occ[c][r2]
    old = cell_cost(o) + (cell_cost(p) if p else 0)
    row[o] = r2
    if p: row[p] = r1
    new = cell_cost(o) + (cell_cost(p) if p else 0)
    row[o] = r1
    if p: row[p] = r2
    return new - old


def do_swap(o, r2):
    c = col_of[o]; r1 = row[o]; p = occ[c][r2]
    row[o] = r2; occ[c][r2] = o
    if p: row[p] = r1
    occ[c][r1] = p


def anneal(rng, tlimit):
    initial(rng)
    cost = total_cost()
    it = 0
    tabu = {}
    while it < ITERS:
        if (it & 255) == 0:
            if time.time() > tlimit: break
            viol = [(s, u) for s, u in edges1 if ecost(s, u) > 0]
            if not viol: return 0, it
        s, u = viol[rng.randrange(len(viol))]
        o = s if rng.random() < 0.5 else u
        c = col_of[o]; w = widths[c]
        if rng.random() < PNOISE:
            r2 = rng.randrange(w)
            if r2 == row[o]: it += 1; continue
            d = swap_delta(o, r2)
        else:
            best = None; bestr = []
            for r2 in range(w):
                if r2 == row[o] or tabu.get((o, r2), -1) > it: continue
                d = swap_delta(o, r2)
                if best is None or d < best: best, bestr = d, [r2]
                elif d == best: bestr.append(r2)
            if best is None: it += 1; continue
            d = best; r2 = bestr[rng.randrange(len(bestr))]
        if d <= 0 or rng.random() < math.exp(-d / T0):
            tabu[(o, row[o])] = it + 10
            do_swap(o, r2); cost += d
        it += 1
        if (it % 20000) == 0:
            print(f"    it={it} cost={cost} viol={n_viol()} ({time.time()-t0:.0f}s)", flush=True)
    return total_cost(), it


t0 = time.time()
deadline = t0 + ATIME
rng = random.Random(SEED)
restart = 0
final = None
while time.time() < deadline:
    restart += 1
    cost, it = anneal(rng, deadline)
    print(f"  restart{restart}: cost={cost} viol={n_viol()} iters={it} ({time.time()-t0:.0f}s)", flush=True)
    if cost == 0:
        final = 0; break
elapsed = time.time() - t0
if final == 0:
    assert n_viol() == 0
    print(f"結果: FEASIBLE ({elapsed:.0f}s)  gap1={len(edges1)} skip={nskip}  restart={restart}"
          f"  外部入力需要(段:相異PI)={ {c: len(p) for c, p in sorted(pi_at.items())} }", flush=True)
    json.dump({'col': col_of, 'row': {o: row[o] for o in cbo}},
              open(f'place_sa_fixed_{CKT}.json', 'w'), ensure_ascii=False)
    print(f"  保存: place_sa_fixed_{CKT}.json")
else:
    print(f"結果: UNKNOWN ({elapsed:.0f}s)  gap1={len(edges1)} skip={nskip}  残り違反={n_viol()}  restart={restart}", flush=True)
