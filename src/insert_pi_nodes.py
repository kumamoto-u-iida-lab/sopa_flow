#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""insert_pi_nodes.py — （2026-10-14）外部入力（PI）を IMUX に直接配らず、PA ノードで運ぶネットリストを作る。

■ 考え方（ユーザー案 (ii)）
  PI ごとに PI ノード（.subckt cell I_a=<PI> I_b=$true, MODE 00 → 出力 = PI、中継と同じ形）を
  構造の一番上の行 TOP（FF 側から数えて、既定 19 = 20段構造の入力側の段0）に1個置く。
  そこから中継の鎖（共有、1本）で、その PI を読むセルのうち FF に最も近い行 h_min の1つ上まで下ろす。
  行 h のセルは、PI の代わりに「行 h+1 にある鎖のノード」を読む。
  → 段1 以降の IMUX に外部入力（EXT）の線が要らない（構造は NEXT=0、段0 の PA は外部ピン I を直受け）。
  増えるノード = PI 1本につき TOP − h_min 個。段数はどの回路も TOP+1 になる。
■ 行（FF 側から）は段固定と同じ: R（FF までの最長距離）、組合せPO を出すセルは 0。
  作った後に load() で行を計算し直し、ノードが狙いの行に、元のセルが元の行にあることを確かめる（ずれたら止める）。
 ★2026-10-20 TOP=local: PI ノードを回路ごとに「論理の一番上の行の1つ上」（行 D_回路）に置く（ユーザー案）。
   構造側は全行の ia に専用の EXT を1本足す（gen_cone_ext.py EXTDED）。増えるノード = PI 1本につき D_回路 − h_min 個。
 使い方: python3 insert_pi_nodes.py [回路名...]
 環境:   EBDIR（入力, 既定 results/eblif_relay） OUTDIR（既定 results/eblif_pinode） TOP（既定 19）
"""
import sys, os, re
from collections import defaultdict
SD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SD)
from place_greedy import load
from annotate_row import comb_po_cells

ROOT = os.path.dirname(SD)
EBDIR = os.environ.get("EBDIR", os.path.join(ROOT, "results", "eblif_relay"))
OUTDIR = os.environ.get("OUTDIR", os.path.join(ROOT, "results", "eblif_pinode"))
TOPENV = os.environ.get("TOP", "19")
LOCAL = TOPENV == "local"
TOP = 0 if LOCAL else int(TOPENV)


def rows_of(eb):
    logic, cbo, R, nff = load(eb)
    row = {o: R[o] for o in cbo}
    for o in comb_po_cells(eb, cbo): row[o] = 0
    return row


def one(c):
    eb = os.path.join(EBDIR, c, f"mapped_{c}.v.eblif")
    lines = open(eb).read().splitlines()
    row = rows_of(eb)
    pis = set(next(l for l in lines if l.startswith('.inputs')).split()[1:])
    TOP = max(row.values()) + 1 if LOCAL else globals()['TOP']   # local: 論理の一番上の1つ上
    if max(row.values()) + 1 > TOP:
        return f"{c}: 段数 {max(row.values()) + 1} が TOP={TOP} 以上なので不可"
    # PI を読むセルと h_min
    hmin = {}
    for l in lines:
        if l.startswith('.subckt cell'):
            p = dict(t.split('=', 1) for t in l.split()[2:])
            o = p['O_a']
            if o not in row: continue
            for x in (p.get('I_a'), p.get('I_b')):
                if x in pis: hmin[x] = min(hmin.get(x, 99), row[o])
    node = lambda x, r: f"{x}__pi{r}"
    out = []; i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('.subckt cell'):
            parts = l.split(); p = dict(t.split('=', 1) for t in parts[2:]); o = p['O_a']
            if o in row:
                for k in ('I_a', 'I_b'):
                    if p.get(k) in hmin: p[k] = node(p[k], row[o] + 1)
                l = ' '.join(parts[:2] + [f"{k}={v}" for k, v in p.items()])
        if l.strip() == '.end':
            for x in sorted(hmin):                    # PI ノード（行 TOP）と鎖（行 TOP-1 .. h_min+1）
                for r in range(TOP, hmin[x], -1):
                    src = x if r == TOP else node(x, r + 1)
                    out.append(f".subckt cell I_a={src} I_b=$true O_a={node(x, r)}")
                    out.append(".param MODE 00")
        out.append(l); i += 1
    od = os.path.join(OUTDIR, c); os.makedirs(od, exist_ok=True)
    ob = os.path.join(od, f"mapped_{c}.v.eblif")
    open(ob, 'w').write('\n'.join(out) + '\n')
    # 検算: 行を計算し直す
    row2 = rows_of(ob)
    bad = [o for o in row if row2.get(o) != row[o]]
    bad += [node(x, r) for x in hmin for r in range(TOP, hmin[x], -1) if row2.get(node(x, r)) != r]
    tops = {node(x, TOP) for x in hmin}               # PI を読むのは行 TOP の PI ノードだけのはず
    for l in open(ob):
        if l.startswith('.subckt cell'):
            p = dict(t.split('=', 1) for t in l.split()[2:])
            if p['O_a'] in row2 and p['O_a'] not in tops and (p.get('I_a') in pis or p.get('I_b') in pis):
                bad.append(p['O_a'])
    add = sum(TOP - h for h in hmin.values())
    if bad:
        return f"{c}: ★行がずれた {len(bad)} 個（例 {bad[:3]}）"
    return f"{c}: セル {len(row)} → {len(row2)}（+{add}、PI {len(hmin)} 本）  段数 {max(row2.values()) + 1}"


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(os.listdir(EBDIR))
    for c in names:
        if os.path.exists(os.path.join(EBDIR, c, f"mapped_{c}.v.eblif")): print(one(c), flush=True)
