#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""annotate_row.py — （2026-10-14）中継入り eblif の各セルに行（段）を書き込んだ「見る用」の eblif と、
   数える用の csv を作る。外部入力（PI）がどの行に入るかを数えるため。

■ 行の決め方（段固定と同じ。FF 側を 0 とする）
   行 = R = そのセルから FF（または PO）までの最長距離（place_greedy.load と同じ計算）
   組合せPO を出すセルは R に関係なく 行 0（place_span_tbl.comb_po_cells と同じ規則）
   → 段固定（place_fixed_tbl.py）で置かれる行そのもの（構造の段番号 col = D-1-行）
■ 出力
   <OUTDIR>/<回路>/mapped_<回路>.v.eblif   セルの .param MODE の次に「.attr row <行>」を足しただけ。
       ★見る用。dup_fanout.py などは「.subckt の次の1行が .param」を前提にしているので、配置配線には元の eblif を使う。
   <OUTDIR>/<回路>/rows_<回路>.csv          1行1セル:
       cell, row, pi_in, clkrst_in, const_in, relay
       pi_in     = そのセルが読む PI の本数（0〜2。clk/rst 系は除く）
       clkrst_in = FF のクロック・リセットにつながる PI、またはそれを反転したセルの出力を読む本数
       const_in  = 定数（$true / $false）を読む本数（PI には数えない。構造では IMUX の定数2本で受ける）
       relay     = 中継セル（insert_relay.py が足した、名前が __r<数字> で終わるもの）なら 1
   <OUTDIR>/index.csv                       回路, 段数D, セル数, 中継数, PIを読むセル数
 使い方: python3 annotate_row.py [回路名...]
 環境:   EBDIR（入力, 既定 results/eblif_relay） OUTDIR（既定 <EBDIR>_row）
"""
import sys, os, re, glob, csv
SD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SD)
from place_greedy import load, CONST

ROOT = os.path.dirname(SD)
EBDIR = os.environ.get("EBDIR", os.path.join(ROOT, "results", "eblif_relay"))
OUTDIR = os.environ.get("OUTDIR", EBDIR.rstrip('/') + "_row")
RELAY = re.compile(r'__r\d+$')


def comb_po_cells(eb, cbo):
    """組合せPO(出力のうちDFF Qでない)を出力するcboセル（place_span_tbl.py と同じ）"""
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
        while s in conn and s not in seen:
            seen.add(s); s = conn[s]
        return s
    res = set()
    for p in pos:
        if p in dffq: continue
        q = p if p in cbo else rz(p)
        if q in cbo and q not in dffq: res.add(q)
    return res


def one(eb, odir):
    lines = open(eb).read().splitlines()
    logic, cbo, R, nff = load(eb)
    row = {o: R[o] for o in cbo}
    for o in comb_po_cells(eb, cbo): row[o] = 0
    pis = set(); dffs = []; cells = {}; consts = {}
    for l in lines:
        s = l.strip()
        if s.startswith('.inputs'): pis = set(s.split()[1:])
        elif s.startswith('.subckt DFF'): dffs.append(dict(t.split('=', 1) for t in s.split()[2:]))
        elif s.startswith('.subckt cell'):
            p = dict(t.split('=', 1) for t in s.split()[2:])
            raw = [x for x in (p.get('I_a'), p.get('I_b')) if x]
            cells[p['O_a']] = [x for x in raw if x not in CONST]
            consts[p['O_a']] = sum(1 for x in raw if x in ('$true', '$false'))
    cr = {d['C'] for d in dffs} | {d['R'] for d in dffs}          # クロック・リセットの信号
    crsrc = set(cr)
    for o in cr:                                                   # それを作るセル（反転など）の入力 PI も clk/rst 系
        crsrc |= set(cells.get(o, []))
    clkrst = (pis & crsrc) | {o for o in cells if o in cr}
    # 見る用 eblif
    out = []; i = 0
    while i < len(lines):
        s = lines[i].strip(); out.append(lines[i])
        if s.startswith('.subckt cell'):
            o = dict(t.split('=', 1) for t in s.split()[2:])['O_a']
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('.param'):
                i += 1; out.append(lines[i])
            if o in row: out.append(f".attr row {row[o]}")
        i += 1
    os.makedirs(odir, exist_ok=True)
    name = os.path.basename(eb)
    ckt = name.replace('mapped_', '').replace('.v.eblif', '')
    open(os.path.join(odir, name), 'w').write('\n'.join(out) + '\n')
    nrel = npi = 0
    with open(os.path.join(odir, f"rows_{ckt}.csv"), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['cell', 'row', 'pi_in', 'clkrst_in', 'const_in', 'relay'])
        for o in sorted(row, key=lambda o: (row[o], o)):
            ins = cells[o]
            pi_in = sum(1 for x in ins if x in pis and x not in clkrst)
            cr_in = sum(1 for x in ins if x in clkrst)
            rl = 1 if RELAY.search(o) else 0
            nrel += rl; npi += (pi_in > 0)
            w.writerow([o, row[o], pi_in, cr_in, consts[o], rl])
    return ckt, max(row.values()) + 1, len(row), nrel, npi


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(os.listdir(EBDIR))
    res = []
    for c in names:
        eb = os.path.join(EBDIR, c, f"mapped_{c}.v.eblif")
        if not os.path.exists(eb): print(f"なし: {eb}"); continue
        r = one(eb, os.path.join(OUTDIR, c)); res.append(r)
        print(f"{r[0]:<12} D={r[1]:>3}  セル {r[2]:>5}  中継 {r[3]:>5}  PIを読むセル {r[4]:>4}", flush=True)
    with open(os.path.join(OUTDIR, "index.csv"), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['circuit', 'D', 'cells', 'relays', 'cells_reading_PI']); w.writerows(res)
    print(f"{len(res)} 回路 → {OUTDIR}")
