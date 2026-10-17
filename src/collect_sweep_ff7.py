#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_sweep_ff7.py — run_sweep_ff7.sh の結果を「回路 × 倍率」の表にまとめる。2026-10-17。
  各セル: 段固定で載った=F / 案B で載った=B / 載らない証明=X（INFEASIBLE）/ 決着せず=U（UNKNOWN 等）/ 未実行=-
  使用率 = その回路の配置対象セル数（論理＋中継＋PI ノード、data/eblif_pinode を place_greedy.load で数える）÷ 構造の PA 数
 出力: results/sweep_ff7/sweep_ff7.csv（1行 = 回路×倍率）と、倍率ごとの集計を標準出力に
 使い方: python3 src/collect_sweep_ff7.py
"""
import os, re, csv, sys
SD = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SD)
sys.path.insert(0, SD)
from place_greedy import load

RES = os.path.join(ROOT, "results", "sweep_ff7")
EBR = os.path.join(ROOT, "data", "eblif_pinode")


def struct_of(s):
    n = "superset_r1536pi_ff7_alt_cyc.v" if s == "1263" else f"superset_pi_ff7_s{s}_alt_cyc.v"
    t = open(os.path.join(ROOT, "structures", n)).read(2000)
    w = [int(x) for x in re.search(r'widths\([^)]*\)=\s*\[([0-9,\s]*)\]', t).group(1).split(',')]
    return sum(w), int(re.search(r'CONFIG=(\d+)', t).group(1))


def status(d, c):
    def res(f):
        p = os.path.join(d, f)
        if not os.path.exists(p): return None
        m = re.search(r'^結果: (\S+)', open(p).read(), re.M)
        return m.group(1) if m else "none"
    a, b = res(f"{c}_fixed.log"), res(f"{c}_B.log")
    if a is None: return "-"
    if a.startswith(("OPTIMAL", "FEASIBLE")) and not a.startswith("INFEASIBLE"): return "F"
    if b and b.startswith(("OPTIMAL", "FEASIBLE")) and not b.startswith("INFEASIBLE"): return "B"
    if (b or a).startswith("INFEASIBLE"): return "X"
    return "U" if b else "-"


cells = {c: len(load(os.path.join(EBR, c, f"mapped_{c}.v.eblif"))[1]) for c in sorted(os.listdir(EBR))}
scales = sorted((d[1:] for d in os.listdir(RES) if re.fullmatch(r's\d+', d)), key=int) if os.path.isdir(RES) else []
rows = []
print(f"{'倍率':>6} {'PA':>5} {'bit':>6} | 段固定 案B 計 /41 | 載らない証明 決着せず 未実行")
for s in scales:
    pa, bits = struct_of(s); d = os.path.join(RES, f"s{s}"); cnt = {}
    for c, n in cells.items():
        st = status(d, c); cnt[st] = cnt.get(st, 0) + 1
        rows.append({"scale": int(s) / 100 if s != "1263" else 1.263, "PA": pa, "bits": bits, "circuit": c,
                     "cells": n, "util": round(n / pa, 4), "status": st})
    f, b = cnt.get("F", 0), cnt.get("B", 0)
    print(f"{rows[-1]['scale']:6.3f} {pa:5d} {bits:6d} | {f:6d} {b:4d} {f + b:3d}/41 | {cnt.get('X', 0):12d} {cnt.get('U', 0):8d} {cnt.get('-', 0):6d}")
os.makedirs(RES, exist_ok=True)
with open(os.path.join(RES, "sweep_ff7.csv"), "w", newline="") as fp:
    w = csv.DictWriter(fp, fieldnames=["scale", "PA", "bits", "circuit", "cells", "util", "status"]); w.writeheader(); w.writerows(rows)
print(f"→ {os.path.join(RES, 'sweep_ff7.csv')}（{len(rows)} 行）")
