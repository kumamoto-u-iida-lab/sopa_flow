#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""select_pa_budget.py — PA 数の予算（例 768）に合わせて、対象回路を選び、列数を決める（2026-10-20）。

■ 手順（ユーザー決定）
  ① PI ノード入りネットリスト（data/eblif_pinode）の「配置する PA 数」（load() の数え方、clk/rst の NOT は含めない）
     が BUDGET 以下の回路を候補にする。
  ② 候補の行ごとの最大（包絡線、FF 側でそろえた20行）を取り、合計が BUDGET / MARGIN 以下になるまで、
     PA 数の大きい回路から順に外す。
     ※ KEEP に回路名を並べると、外した後に戻す（768 では MARGIN=1.2 で 25回路→ micks を戻して 26回路、余白 1.18倍）。
  ③ 列数（肉付け）: ff7 と同じ決まり
       行0（FF）= 7 固定 / 最上段 = 包絡線のまま（PI の最大本数＝外部入力バスの本数）
       行1〜18 = ⌈包絡線 × f⌉、FF 側から「入力側の行 ≤ 2 × FF 側の隣」、逆向きに「FF 側の行 ≥ 入力側の隣 / 2」
       合計が BUDGET になる最大の f を二分探索で探す（端数は f を上げたとき先に増える行に +1）。
 使い方: BUDGET=768 MARGIN=1.2 KEEP=micks python3 select_pa_budget.py
         → 回路の一覧・包絡線・列数（FF 側→入力側）を表示、OUT（既定 results/pa<BUDGET>_select.json）に保存
         列数を gen_cone_ext.py に渡す（TOPEXT=1 CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0×20 NEXTTAG=pinode）。
"""
import os, sys, json, math
SD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SD)
from place_greedy import load
from annotate_row import comb_po_cells

ROOT = os.path.dirname(SD)
EBDIR = os.environ.get("EBDIR", os.path.join(ROOT, "data", "eblif_pinode"))
BUDGET = int(os.environ.get("BUDGET", "768"))
MARGIN = float(os.environ.get("MARGIN", "1.2"))
KEEP = [c for c in os.environ.get("KEEP", "").split(",") if c]
FF0 = int(os.environ.get("FF0", "7"))
NROW = 20
OUT = os.environ.get("OUT", os.path.join(ROOT, "results", f"pa{BUDGET}_select.json"))

N, U = {}, {}
for c in sorted(os.listdir(EBDIR)):
    eb = os.path.join(EBDIR, c, f"mapped_{c}.v.eblif")
    if not os.path.exists(eb): continue
    logic, cbo, R, nff = load(eb)
    row = {o: R[o] for o in cbo}
    for o in comb_po_cells(eb, cbo): row[o] = 0
    u = [0] * NROW
    for v in row.values(): u[v] += 1
    N[c], U[c] = len(row), u
env = lambda S: [max(U[c][h] for c in S) for h in range(NROW)]

S = sorted([c for c in N if N[c] <= BUDGET], key=lambda c: N[c])
print(f"① PA ≤ {BUDGET}: {len(S)} 回路（外れた: {' '.join(c for c in sorted(N, key=N.get) if N[c] > BUDGET)}）")
removed = []
while sum(env(S)) > BUDGET / MARGIN:
    removed.append(S.pop())
print(f"② 包絡線 ≤ {BUDGET}/{MARGIN} まで外した: {' '.join(removed)}")
for c in KEEP:
    if c not in S: S.append(c)
E = env(S)
print(f"   対象 {len(S)} 回路、包絡線 {sum(E)}（余白 {BUDGET / sum(E):.3f} 倍）: {E}")


def build(f):
    w = [FF0] + [math.ceil(E[h] * f) for h in range(1, NROW - 1)] + [E[NROW - 1]]
    for h in range(1, NROW): w[h] = min(w[h], 2 * w[h - 1])
    for h in range(NROW - 2, 0, -1): w[h] = max(w[h], math.ceil(w[h + 1] / 2))
    return w


lo, hi = 1.0, 3.0
for _ in range(80):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if sum(build(m)) <= BUDGET else (lo, m)
w = build(lo); nxt = build(hi)
for h in [h for h in range(1, NROW - 1) if nxt[h] > w[h]][:BUDGET - sum(w)]: w[h] += 1
assert sum(w) == BUDGET and all(max(a, b) <= 2 * min(a, b) for a, b in zip(w, w[1:]))
print(f"③ 列数（FF 側→入力側, f={lo:.4f}）: {w}  計 {sum(w)}")
print(f"   gen_cone_ext.py の引数: {','.join(map(str, w))}")
print(f"   回路（CKTS）: {' '.join(sorted(S, key=N.get))}")
json.dump({"budget": BUDGET, "margin": MARGIN, "circuits": sorted(S, key=N.get), "pa": {c: N[c] for c in S},
           "env": E, "widths_ff_to_in": w, "f": lo}, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"   → {OUT}")
