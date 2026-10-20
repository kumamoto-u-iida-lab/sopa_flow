#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""envelope_widths.py — ネットリスト群の包絡線（行ごとの最大、FF 側でそろえる）× 倍率 で列数を決める（2026-10-20）。

  列数の決まり（ff7 と同じ）: 行0（FF）= FF0 固定、他の行は ⌈包絡線 × SCALE⌉、
  FF 側から「入力側の行 ≤ 2 × FF 側の隣」、逆向きに「FF 側の行 ≥ 入力側の隣 / 2」。
  最上段も倍率をかける（EXTDED 構造では最上段も普通の行と同じく PI ノードの置き場なので）。
 使い方: EBDIR=data/eblif_pilocal NROW=19 SCALE=1.2 python3 envelope_widths.py
         → 1行目に gen_cone_ext.py の引数（FF 側→入力側）、標準エラーに包絡線と合計
"""
import os, sys, math
SD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SD)
from place_greedy import load
from annotate_row import comb_po_cells

ROOT = os.path.dirname(SD)
EBDIR = os.environ.get("EBDIR", os.path.join(ROOT, "data", "eblif_pilocal"))
if not os.path.isabs(EBDIR): EBDIR = os.path.join(ROOT, EBDIR)
NROW = int(os.environ.get("NROW", "19"))
SCALE = float(os.environ.get("SCALE", "1.2"))
FF0 = int(os.environ.get("FF0", "7"))

E = [0] * NROW
for c in sorted(os.listdir(EBDIR)):
    eb = os.path.join(EBDIR, c, f"mapped_{c}.v.eblif")
    if not os.path.exists(eb): continue
    logic, cbo, R, nff = load(eb)
    row = {o: R[o] for o in cbo}
    for o in comb_po_cells(eb, cbo): row[o] = 0
    assert max(row.values()) < NROW, f"{c}: 行 {max(row.values())} が NROW={NROW} を超える"
    u = [0] * NROW
    for v in row.values(): u[v] += 1
    E = [max(a, b) for a, b in zip(E, u)]
w = [FF0] + [math.ceil(e * SCALE) for e in E[1:]]
for h in range(1, NROW): w[h] = min(w[h], 2 * w[h - 1])
for h in range(NROW - 2, 0, -1): w[h] = max(w[h], math.ceil(w[h + 1] / 2))
assert all(max(a, b) <= 2 * min(a, b) for a, b in zip(w, w[1:]))
print(','.join(map(str, w)))
print(f"包絡線 {sum(E)} {E}\n×{SCALE} → {sum(w)} {w}", file=sys.stderr)
