#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dup_fanout.py — （2026-09-15）中継入り eblif で fanout(次段の相異なる読み手セル数) が MAXF を超えるセルを複製して MAXF 以下にする。
   FF側の段から入力側へ処理（コピーは元と同じ入力を読むので親の fanout が増える → 親も後で処理される）。
   使い方: python3 dup_fanout.py <in eblif> <out eblif>   環境: MAXF(既定2)
"""
import sys,os,re,math
from collections import defaultdict,Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place_greedy import load
IN,OUT=sys.argv[1],sys.argv[2]; MAXF=int(os.environ.get("MAXF","2"))
lines=open(IN).read().splitlines()
# セル定義を読む（.subckt cell の行と直後の .param MODE）
cells={}; order=[]; other=[]; i=0
while i<len(lines):
    s=lines[i].strip()
    if s.startswith('.subckt cell'):
        p=dict(t.split('=',1) for t in s.split()[2:]); mode=lines[i+1] if i+1<len(lines) and lines[i+1].strip().startswith('.param') else None
        cells[p['O_a']]=dict(I_a=p.get('I_a'),I_b=p.get('I_b'),mode=mode); order.append(p['O_a']); i+=2 if mode else 1; continue
    other.append(lines[i]); i+=1
lg,cb,R,nff=load(IN); D=max(R.values())+1
pos=[];dffq=set();dffd=set()
for l in lines:
    s=l.strip()
    if s.startswith('.outputs'): pos=s.split()[1:]
    elif s.startswith('.subckt DFF'):
        d=dict(x.split('=',1) for x in s.split()[2:]); dffq.add(d.get('Q')); dffd.add(d.get('D'))
col={o:D-1-R[o] for o in cb}
for p in pos:
    if p in cb and p not in dffq: col[p]=D-1
sinks=set(pos)|dffd                     # 元の名前を残す必要がある出力
before=Counter()
w_before=Counter(col.values())   # 複製前の段別セル数
def readers():
    rd=defaultdict(list)
    for u,c in cells.items():
        if u not in col: continue
        for pin in ('I_a','I_b'):
            s=c[pin]
            if s in col and col[u]-col[s]==1 and u not in rd[s]: rd[s].append(u)
    return rd
for o,lst in readers().items(): before[len(lst)]+=1
added=Counter(); ncopy=0
for stage in range(D-2,-1,-1):
    rd=readers()
    for o in [x for x in list(cells) if col.get(x)==stage]:
        lst=rd.get(o,[])
        if len(lst)<=MAXF: continue
        groups=[lst[j:j+MAXF] for j in range(0,len(lst),MAXF)]
        for gi,grp in enumerate(groups[1:],1):
            nm=f"{o}__d{gi}"
            cells[nm]=dict(I_a=cells[o]['I_a'],I_b=cells[o]['I_b'],mode=cells[o]['mode']); col[nm]=stage
            for u in grp:
                for pin in ('I_a','I_b'):
                    if cells[u][pin]==o: cells[u][pin]=nm
            added[stage]+=1; ncopy+=1
out=[]
for l in other:
    if l.strip()=='.end':
        for o,c in cells.items():
            out.append(f".subckt cell I_a={c['I_a']} I_b={c['I_b']} O_a={o}")
            if c['mode']: out.append(c['mode'])
    out.append(l)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w').write('\n'.join(out)+'\n')
# 検算
lg2,cb2,R2,_=load(OUT); D2=max(R2.values())+1; col2={o:D2-1-R2[o] for o in cb2}
for p in pos:
    if p in cb2 and p not in dffq: col2[p]=D2-1
rd2=defaultdict(set); gapbad=0
for x in lg2:
    for s in x['srcs']:
        if s in cb2:
            g=col2[x['o']]-col2[s]
            if g==1: rd2[s].add(x['o'])
            elif g>=2: gapbad+=1
after=Counter(len(v) for v in rd2.values())
w1=w_before; w2=Counter(col2.values())
print(f"fanout 分布（前）: {dict(sorted(before.items()))}")
print(f"fanout 分布（後）: {dict(sorted(after.items()))}   最大 {max(after)}")
print(f"複製したセル: {ncopy} 個  段別: {dict(sorted(added.items()))}")
print(f"セル数 {len(cb)} → {len(cb2)}   段数 D {D} → {D2}   段飛び残り {gapbad}")
print(f"段別セル数（前）: {[w1[c] for c in range(D)]}")
print(f"段別セル数（後）: {[w2[c] for c in range(D2)]}")
