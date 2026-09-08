#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_superset.py — 41回路の包絡線から【スーパーセット構造】を1つ生成する。

2026-08-31 作成。先生の 8/21 指示①②「乗ると絞った27回路でなく、
全回路が載る構造1つで言え」への答えを作るためのもの。

■ 設計（2026-08-31 ユーザー決定）
  段の対応づけ  案1【FF側で揃える】: 回路xの段k → 超集合の段 k + (D - D_x)
                出発段も行き先段も同じだけずれるので【距離 d は不変】
  母数          41回路（ass13_no_decoder / proc16816_ff1 / proc16816_ff3 を除外）
  段数D         max(D_x)          各段の幅  各段での max
  FF枠          最下段の幅 = max  外部入力  max(|PI|) を全段一律
  skip          案A【(行き先段c, 距離d) ごとに max】= 粒度最細 = 一番細い構造

■ 使い方
    python3 superset_profile.py     # 先に包絡線を数えて superset_profile.json を作る
    python3 gen_superset.py         # それを読んで構造 .v を生成する
  環境変数: PROFILE(既定 superset_profile.json) / OUT(既定 superset.v) / TAG

■ ⚠️ 机上では潰せない危険点（2026-08-24 に確認）
  隣接候補 cand[段k][行r] は幅から自動生成される（gen_pattern の A_k ルール）。
  幅を広げると cand のパターンが変わるので、広い構造の cand が狭い構造の cand の
  【上位集合とは限らない】。よって「項目ごとに max を取れば全部載る」は保証されない。
  → 作って41回路を回して確かめるしかない。落ちたら幅か skip を足す。
"""
import os, sys, json, subprocess, shutil

SD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SD)
PROFILE = os.environ.get("PROFILE", os.path.join(ROOT, "results", "superset_profile.json"))
OUT = os.environ.get("OUT", os.path.join(ROOT, "results", "superset.v"))
TAG = os.environ.get("TAG", "superset")

with open(PROFILE, encoding="utf-8") as f:
    P = json.load(f)

D = P["D"]
widths = [P["env_width"][str(k)] for k in range(D)]          # 入力側 -> FF側
# ★2026-09-09: 余白。MARGIN_SPEC="8-13:3" なら 段8〜13 の幅に +3（複数は ; 区切り）。
#   全中継の超集合で中継が集中する中段（9/3: 段12→13 の結合で詰まる）に空き枠を足し、
#   UNKNOWN 15回路が載るかを試すためのもの。config は 1枠 ≈ 2+2·⌈log2 n⌉ bit、面積 ≈ 1.2k μm² 増える。
MARGIN_SPEC = os.environ.get("MARGIN_SPEC", "")
if MARGIN_SPEC:
    for spec in MARGIN_SPEC.split(";"):
        rng, m = spec.split(":"); a, b = (rng.split("-") + [rng])[:2]
        for k in range(int(a), int(b) + 1):
            widths[k] += int(m)
    print(f"余白 MARGIN_SPEC={MARGIN_SPEC} → 幅 {widths}")
n_pi = P["pi_max"]
env_skip = P["env_skip"]                                      # "c,d" -> 本数

print(f"段数 D = {D}")
print(f"段別幅(入力側->FF側) = {widths}")
print(f"総PA数 = {sum(widths)}   最下段(FF枠) = {widths[-1]}   |PI| = {n_pi}")
print(f"skip = {sum(env_skip.values())}本 / {len(env_skip)}通りの(行き先段,距離)")

# ---- gen_cone_ext.py へ渡す形に整える ----
# 幅は「FF側->入力側」の順で位置引数
ff_to_in = ",".join(str(w) for w in reversed(widths))
# SKIPMAP="c,d,cnt;..."（行き先段c, 距離d, 本数cnt）
skipmap = ";".join(f"{k},{v}" for k, v in
                   ((key, cnt) for key, cnt in sorted(
                       env_skip.items(), key=lambda x: tuple(int(t) for t in x[0].split(",")))))
# 外部入力は段0を除いて一律 |PI|（回路ごとの構造と同じ流儀）
next_ext = [0] + [n_pi] * (D - 1)

env = dict(os.environ, SKIPMAP=skipmap,
           NEXT=",".join(map(str, next_ext)), NEXTTAG=TAG)
if not env_skip:
    # ★2026-09-02: skip 0本の包絡線（中継挿入済み eblif から作ったもの）。
    #   SKIPMAP が空だと gen_cone_ext.py は固定 SKIP_SPECS(4/2/1本) に戻ってしまうので、
    #   ここで明示的に「skip 0本」を渡す。
    env["SKIP_SPECS"] = "2:0"
    print("  skip 0本 → SKIP_SPECS=2:0 を渡す（skip無し構造）")

print(f"\ngen_cone_ext.py を呼ぶ:")
print(f"  幅(FF側->入力側) = {ff_to_in}")
print(f"  SKIPMAP  = {len(env_skip)}項目")
print(f"  NEXT     = 段0は0、以降 {n_pi} 一律\n")

r = subprocess.run([sys.executable, os.path.join(SD, "gen_cone_ext.py"), ff_to_in],
                   cwd=SD, capture_output=True, text=True, env=env)
print(r.stdout.strip())
if r.returncode != 0:
    print("★失敗\n" + r.stderr.strip()[-2000:])
    sys.exit(1)

src = os.path.join(SD, "cone_spindle_" + "-".join(str(w) for w in reversed(widths)) + f"_{TAG}.v")
if not os.path.exists(src):
    print(f"★生成物が見つからない: {src}")
    sys.exit(1)
shutil.move(src, OUT)
png = src[:-2] + ".png"
if os.path.exists(png):
    shutil.move(png, OUT[:-2] + ".png")
print(f"\n→ {OUT}")
with open(OUT, encoding="utf-8") as f:
    for line in [next(f), next(f)]:
        print("  " + line.rstrip())
