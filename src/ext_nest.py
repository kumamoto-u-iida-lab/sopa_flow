#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ext_nest.py — （2026-10-14）外部入力（EXT）を段ごとに先頭 n 本だけ配る構造のための、PI → EXT 線の割り当て。

■ 構造（gen_cone_ext.py）: 構造の段 c（入力側から）には EXT[0..next_ext[c]-1] の先頭だけが配られる。
  例 1,536PA ext45n: FF側から 行0〜4=12本 / 5〜9=24本 / 10〜14=36本 / 15〜19=45本（行19=構造の段0 は PI 直受け）
■ 条件（入れ子）: PI → EXT 線は回路で1通り。枠が k 本以下の行で使う PI の和集合が k 本以下（k = 枠の各値）。
■ 割り当て: PI を「使う行のうち最も小さい枠」の小さい順に並べ、EXT[0] から詰める。
  条件を満たす限りこれで必ず割り当てられる（枠の小さい行で要る PI ほど前に来るため）。
行 h は FF 側から（h = D-1-c）。構造の段0（c=0）は PI を直接受けるので対象外。
"""


def tap(h, D, next_ext):
    """行 h に配られる EXT の本数。構造の段0（直受け）は None（制限なし）。"""
    c = D - 1 - h
    return None if c == 0 else next_ext[c]


def check(pi_rows, D, next_ext):
    """pi_rows: {PI: 使う行の集合}。入れ子の条件を満たさない最初の (枠k, 必要本数) を返す。満たせば None。"""
    levels = sorted({next_ext[c] for c in range(1, D)})
    for k in levels:
        need = {p for p, hs in pi_rows.items() if any((t := tap(h, D, next_ext)) is not None and t <= k for h in hs)}
        if len(need) > k:
            return k, len(need)
    return None


def assign(pi_rows, D, next_ext):
    """{PI: EXT番号}。構造の段0 だけで使う PI は EXT を使わないので含めない。条件を満たさなければ None。"""
    if check(pi_rows, D, next_ext): return None
    key = {}
    for p, hs in pi_rows.items():
        ts = [t for h in hs if (t := tap(h, D, next_ext)) is not None]
        if ts: key[p] = min(ts)
    order = sorted(key, key=lambda p: (key[p], p))
    return {p: i for i, p in enumerate(order)}


def verify(pi_rows, D, next_ext, ext):
    """割り当て ext が正しいかの検算。誤りの文字列のリストを返す。"""
    err = []
    if len(set(ext.values())) != len(ext): err.append("EXT番号の重複")
    for p, hs in pi_rows.items():
        for h in hs:
            t = tap(h, D, next_ext)
            if t is None: continue
            if p not in ext: err.append(f"{p}: EXT 割り当て無し（行{h}で使用）")
            elif ext[p] >= t: err.append(f"{p}: EXT[{ext[p]}] は行{h}に届かない（行{h}は先頭{t}本）")
    return err
