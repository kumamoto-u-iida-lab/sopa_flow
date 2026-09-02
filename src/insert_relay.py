#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""insert_relay.py — 段飛び辺をすべて【中継(フィードスルー)セル】に置き換えた eblif を作る。

2026-09-02 作成。「skip配線を一切持たない構造(PA+隣接配線+外部入力だけ)に41回路が載るか」
を試すための手順①。

■ 考え方
  段固定(col = D-1-R, R=FFまでの最長距離)では、段飛び辺「s(段c) → u(段c+g)」の中継が
  どの段に何個要るかは SAT を回さなくても決まる。中継はネットリスト側にセルとして足すだけで、
  行だけ解く既存ツール(place_fixed_skip_ext.py)がそのまま使える。
■ 中継の共有（2026-09-02 ユーザー決定）
  信号ごとに鎖1本。s を段 c+3 と c+5 で読むなら中継は c+1..c+4 の 4個(読み手ごとに別の鎖なら6個)。
  PA出力は次段の全imuxの候補に配られるのでファンアウトは追加コスト0。
■ 中継セルの形（PA.v: O = (A AND (B XOR m0)) XOR m1、MODE=00, I_B=1 → O=A）
  .subckt cell I_a=<信号> I_b=$true O_a=<信号>__r<k>
  .param MODE 00
■ 組合せPOの移動
  配置ツール(place_fixed_skip_ext.py)/生成器(gen_ext_uniform_all.py)は組合せPOセルを最下段へ動かす。
  ここでも同じ規則で動かしてから段飛びを数える。移動先セルの入力に中継を張ると、その中継の R は
  load() の再計算で 1+R(POセル) になる。41回路すべてで「R>0 かつ cbo 入力を段飛びで読む」POセルは無い(2026-09-02 確認済み)。
  該当した場合はここで止める(要対策)。
 使い方: python3 insert_relay.py [回路名...]   環境変数 EBDIR(入力, 既定 data/eblif_from_rtl) / OUTDIR(既定 results/eblif_relay)
"""
import sys, os, re, glob
from collections import defaultdict, Counter
SD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SD)
from place_greedy import load

ROOT = os.path.dirname(SD)
EBDIR = os.environ.get("EBDIR", os.path.join(ROOT, "data", "eblif_from_rtl"))   # sopa_flow: 同梱の41回路eblif
OUTDIR = os.environ.get("OUTDIR", os.path.join(ROOT, "results", "eblif_relay"))
SKIP_CKT = {"ass13_no_decoder", "ass13_tb"}


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


def relay_name(s, k):
    return f"{s}__r{k}"


def process(ckt, eb, out):
    logic, cbo, R, nff = load(eb)
    D = max(R.values()) + 1
    col = {o: (D - 1) - R[o] for o in cbo}
    po = comb_po_cells(eb, cbo)
    for o in po:
        col[o] = D - 1
    for o in po:   # 移動先セルが cbo 入力を段飛びで読み、かつ R>0 なら中継の R がずれる → 止める
        if R[o] > 0 and any(s in cbo and col[o] - col[s] >= 2 for s in cbo[o]['srcs']):
            raise RuntimeError(f"組合せPOセル {o} の R={R[o]}>0 かつ段飛び入力あり。移動後の中継Rがずれるので要対策")
    # 信号ごとの最遠読み手までの距離 → 鎖の長さ
    maxgap = defaultdict(int); nskip = 0
    for c in logic:
        u = c['o']
        for s in c['srcs']:
            if s in cbo and col[u] - col[s] >= 2:
                nskip += 1
                maxgap[s] = max(maxgap[s], col[u] - col[s])
    # 書き換え: 入力の付け替え表 (u, s) -> s__r{g-1}
    rewrite = {}
    for c in logic:
        u = c['o']
        for s in c['srcs']:
            if s in cbo:
                g = col[u] - col[s]
                if g >= 2:
                    rewrite[(u, s)] = relay_name(s, g - 1)
    relays = []   # (name, src, col)
    for s, g in maxgap.items():
        prev = s
        for k in range(1, g):
            nm = relay_name(s, k)
            relays.append((nm, prev, col[s] + k))
            prev = nm
    # eblif を書き出す（.subckt cell の I_a/I_b だけ付け替え、.end の前に中継を追加）
    lines = open(eb).read().splitlines()
    outl = []
    for l in lines:
        st = l.strip()
        if st.startswith('.subckt cell'):
            p = dict(t.split('=', 1) for t in st.split()[2:])
            u = p['O_a']
            for key in ('I_a', 'I_b'):
                if key in p and (u, p[key]) in rewrite:
                    p[key] = rewrite[(u, p[key])]
            l = '.subckt cell ' + ' '.join(f"{k}={v}" for k, v in p.items())
        if st == '.end':
            for nm, src, cc in relays:
                outl.append(f".subckt cell I_a={src} I_b=$true O_a={nm}")
                outl.append(".param MODE 00")
        outl.append(l)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write('\n'.join(outl) + '\n')
    # 検算: 書き出したものを load() し直して段飛びが0か・元セルの段が不変か
    lg2, cb2, R2, nff2 = load(out)
    D2 = max(R2.values()) + 1
    col2 = {o: (D2 - 1) - R2[o] for o in cb2}
    for o in comb_po_cells(out, cb2):
        col2[o] = D2 - 1
    bad = [(u, s) for c in lg2 for u in [c['o']] for s in c['srcs'] if s in cb2 and col2[u] - col2[s] >= 2]   # 後ろ向き辺(移動した組合せPO→前段)はFFfbが吸収するので対象外
    moved = [o for o in cbo if col2.get(o) != col[o]]
    rc = Counter(cc for _, _, cc in relays)
    w_old = Counter(col.values()); w_new = Counter(col2.values())
    print(f"{ckt:10s} D={D} セル{len(cbo)}→{len(cb2)} 中継{len(relays)}個 (段飛び辺{nskip}本, 鎖{len(maxgap)}本)"
          f"  検算: 段飛び残り{len(bad)} / 元セルの段ずれ{len(moved)} / D {D}→{D2}", flush=True)
    print(f"           幅(旧) {[w_old.get(c,0) for c in range(D)]}")
    print(f"           中継   {[rc.get(c,0) for c in range(D)]}")
    print(f"           幅(新) {[w_new.get(c,0) for c in range(D2)]}")
    if bad or moved or D != D2:
        print(f"  ⚠️ 検算NG bad={bad[:3]} moved={moved[:3]}")
    return len(cbo), len(relays), nskip


if __name__ == '__main__':
    sel = set(sys.argv[1:])
    n = 0
    for d in sorted(glob.glob(os.path.join(EBDIR, '*'))):
        ckt = os.path.basename(d)
        if not os.path.isdir(d) or ckt in SKIP_CKT or (sel and ckt not in sel):
            continue
        eb = os.path.join(d, f"mapped_{ckt}.v.eblif")
        if not os.path.exists(eb):
            continue
        process(ckt, eb, os.path.join(OUTDIR, ckt, f"mapped_{ckt}.v.eblif"))
        n += 1
    print(f"=== {n}回路 → {OUTDIR}")
