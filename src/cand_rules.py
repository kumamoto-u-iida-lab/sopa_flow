#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cand_rules.py — 段間の候補表（次段の行 r が前段のどの行から入力を選べるか）の作り方（2026-09-17）
   now    : 今の規則 gen_pattern = A_k=min(N,⌊2N/k⌋)。前段の若い行ほど多くの行に届く（偏りあり）
   cyclic : 巡回。前段の行を 0,s,2s,…(mod ns) と並べた列を先頭から d 個ずつ次段の行0,1,… に配る。
            s は ns と互いに素 → 列は前段の全行を一巡するので、届く回数の差は行ごとに1以内・届かない行ゼロ。
            d = ⌈今の規則の候補総数 / 次段幅⌉（全行同じ d。切り上げのぶん候補が今より 5〜10% 多い）
   alt_now/alt_cyc : 行ごとに今の規則と cyclic_eq を交互に使う（2026-09-22）
   cyclic_eq : ★公平版（2026-09-17）。次段の行 r の候補数を今の規則のその行の数と完全に同じにし、
            つなぎ先だけ巡回で配る（列の先頭から |今の規則の行 r| 個ずつ）。MUX の大きさ・bit 数が今と一致。
            間隔 s は 1行あたり平均候補数 d̄=round(総数/次段幅) から ⌊ns/d̄⌋、ns と互いに素まで −1。
   使い方: from cand_rules import make_cand; make_cand(ns, nd, rule)
"""
import math
from place_greedy import gen_pattern

def make_cand(ns, nd, rule="now", row=None):
    """row = 行き先の行番号。交互規則（alt_now / alt_cyc）のときだけ使う。
       alt_now : row が偶数 → 今の規則、奇数 → 巡回（本数そろえ版）
       alt_cyc : row が偶数 → 巡回、奇数 → 今の規則"""
    if rule in ("alt_now", "alt_cyc"):
        if row is None:
            raise ValueError(f"{rule} には row（行き先の行番号）が要る")
        even_is_now = (rule == "alt_now")
        use_now = (row % 2 == 0) == even_is_now
        return make_cand(ns, nd, "now" if use_now else "cyclic_eq")

    base = gen_pattern(ns, nd)
    if rule == "now":
        return base
    if rule == "cyclic_eq":
        sizes = [len(b) for b in base]
        dbar = max(1, round(sum(sizes) / nd))
        s = max(1, ns // dbar)
        while s > 1 and math.gcd(s, ns) != 1:
            s -= 1
        seq = [(j * s) % ns for j in range(ns)]
        out, p = [], 0
        for k in sizes:
            out.append(sorted({seq[(p + j) % ns] for j in range(k)}))
            p += k
        return out
    if rule != "cyclic":
        raise ValueError(f"未知の CAND_RULE: {rule}")
    d = min(ns, max(1, math.ceil(sum(len(b) for b in base) / nd)))
    s = max(1, ns // d)
    while s > 1 and math.gcd(s, ns) != 1:
        s -= 1
    seq = [(j * s) % ns for j in range(ns)]          # 前段の全行を1回ずつ
    return [sorted({seq[(r * d + j) % ns] for j in range(d)}) for r in range(nd)]

def reach(cand, ns):
    r = [0] * ns
    for row in cand:
        for k in row:
            r[k] += 1
    return r

if __name__ == "__main__":
    import sys
    ns, nd = int(sys.argv[1]), int(sys.argv[2])
    for rule in ("now", "cyclic", "cyclic_eq"):
        c = make_cand(ns, nd, rule)
        rc = reach(c, ns)
        print(f"{rule:<6} 候補{sum(map(len, c))}本  届く先 最大{max(rc)} 最小{min(rc)}  {rc}")
