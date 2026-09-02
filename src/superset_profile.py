#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""superset_profile.py — 41回路のプロファイルを数えて、スーパーセット構造の包絡線を出す。

2026-08-30 作成。手順1（数えるだけ）専用。構造の .v は作らない。

■ 何をするか
  cone_ext_uniform/<回路>.v （回路ごとの「要求ちょうど」構造）から
    - 段別の幅 widths（入力側→FF側）
    - 段数 D_x
    - |PI| (EXTBUS)
    - FF枠 (ff)
    - config 内訳 (pa / imux / skip / ff)
    - skip の (行き先段 c, 距離 d) ごとの本数
  を読み、【FF側で揃えて】項目ごとに max を取る。

■ 段の対応づけ（2026-08-30 ユーザー決定・案1）
    D   = max(D_x) = スーパーセットの段数
    回路xの段 k  →  スーパーセットの段 k + (D - D_x)
    出発段も行き先段も同じだけずれるので【距離 d は不変】。

■ skip の max の取り方（2026-08-30 ユーザー決定・案A）
    (行き先段 c, 距離 d) ごとに max を取る。粒度が一番細かい＝一番細い構造になる。

■ 除外する3本（41回路にするため）
    ass13_no_decoder   ass13 の変種
    proc16816_ff1      proc16816 のFF段違いの変種
    proc16816_ff3      同上
"""
import os, re, sys, math, json

SRC = os.environ.get("SRC") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "cone_ext_uniform")   # 2026-09-02: 環境変数SRCで差し替え可
EXCLUDE = {"ass13_no_decoder", "proc16816_ff1", "proc16816_ff3"}

RE_HEAD = re.compile(
    r"widths\(入力側->FF側\)=\[([^\]]*)\].*?EXTBUS=(\d+)\s+CONFIG=(\d+)bit")
RE_BREAK = re.compile(r"skip=(\d+)\s*/\s*imux=(\d+)\s*/\s*pa=(\d+)\s*/\s*ff=(\d+)")
RE_SKIP = re.compile(r"//\s*skip:\s*行(\d+)→行(\d+)\s*\((\d+)段飛び\)")


def parse(path):
    """1回路ぶんの .v を読んでプロファイルを返す。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()

    m = RE_HEAD.search(text)
    if not m:
        raise ValueError(f"ヘッダを読めない: {path}")
    widths = [int(x) for x in m.group(1).split(",")]
    n_pi = int(m.group(2))
    config = int(m.group(3))

    b = RE_BREAK.search(text)
    if not b:
        raise ValueError(f"config内訳を読めない: {path}")
    bits = dict(skip=int(b.group(1)), imux=int(b.group(2)),
                pa=int(b.group(3)), ff=int(b.group(4)))

    # skip: (行き先段 c, 距離 d) → 本数
    skips = {}
    for src, dst, dist in RE_SKIP.findall(text):
        key = (int(dst), int(dist))
        skips[key] = skips.get(key, 0) + 1

    return dict(widths=widths, D=len(widths), n_pi=n_pi, config=config,
                bits=bits, skips=skips)


def main():
    names = sorted(n[:-2] for n in os.listdir(SRC) if n.endswith(".v"))
    names = [n for n in names if n not in EXCLUDE]
    print(f"対象 {len(names)} 回路（除外 {sorted(EXCLUDE)}）\n")

    prof = {}
    for n in names:
        prof[n] = parse(os.path.join(SRC, f"{n}.v"))

    D = max(p["D"] for p in prof.values())
    print(f"スーパーセットの段数 D = max(D_x) = {D}")
    top = [n for n in names if prof[n]["D"] == D]
    print(f"  D={D} の回路: {top}\n")

    # ---- FF側揃えで各回路を写す ----
    for n, p in prof.items():
        off = D - p["D"]
        p["offset"] = off
        p["w_aligned"] = {off + k: w for k, w in enumerate(p["widths"])}
        p["s_aligned"] = {(c + off, d): cnt for (c, d), cnt in p["skips"].items()}

    # ---- 包絡線 ----
    env_w = {}
    for k in range(D):
        vals = [(p["w_aligned"].get(k, 0), n) for n, p in prof.items()]
        w, who = max(vals)
        env_w[k] = (w, who)

    env_s = {}
    for n, p in prof.items():
        for key, cnt in p["s_aligned"].items():
            if cnt > env_s.get(key, (0, ""))[0]:
                env_s[key] = (cnt, n)

    ff_max = max((p["bits"]["ff"], n) for n, p in prof.items())
    pi_max = max((p["n_pi"], n) for n, p in prof.items())

    # ---- 表示 ----
    print("=== 段ごとの幅の包絡線（FF側揃え。段17が最下段=FF側）===")
    print(f"{'段':>3} {'max幅':>6}  決めた回路")
    for k in range(D):
        w, who = env_w[k]
        print(f"{k:>3} {w:>6}  {who}")
    print(f"\n  総PA数（スーパーセット） = {sum(w for w, _ in env_w.values())}")
    print(f"  各回路の総PA数 min/中央/max = "
          f"{min(sum(p['widths']) for p in prof.values())} / "
          f"{sorted(sum(p['widths']) for p in prof.values())[len(prof)//2]} / "
          f"{max(sum(p['widths']) for p in prof.values())}")

    print(f"\n=== FF枠 = max = {ff_max[0]}（{ff_max[1]}）")
    print(f"=== |PI| = max = {pi_max[0]}（{pi_max[1]}）")

    print(f"\n=== skip の包絡線（(行き先段, 距離) ごとの max）===")
    print(f"{'行き先段':>8}{'距離d':>6}{'max本数':>8}  {'出発段':>6}{'出発段幅':>9}{'bit/本':>7}{'小計bit':>8}  決めた回路")
    tot_tracks = tot_bits = 0
    for (c, d) in sorted(env_s):
        cnt, who = env_s[(c, d)]
        src = c - d
        sw = env_w[src][0] if 0 <= src < D else 0
        per = 0 if sw <= 1 else max(1, math.ceil(math.log2(sw)))
        tot_tracks += cnt
        tot_bits += cnt * per
        print(f"{c:>8}{d:>6}{cnt:>8}  {src:>6}{sw:>9}{per:>7}{cnt*per:>8}  {who}")
    print(f"\n  skip 総本数 = {tot_tracks} 本 / skip 構成メモリ = {tot_bits} bit")
    print(f"  各回路の skip 本数 min/中央/max = "
          f"{min(sum(p['skips'].values()) for p in prof.values())} / "
          f"{sorted(sum(p['skips'].values()) for p in prof.values())[len(prof)//2]} / "
          f"{max(sum(p['skips'].values()) for p in prof.values())}")

    # 後段（Excel化・構造生成）で使えるように JSON で吐く
    out = os.path.join(os.path.dirname(SRC), "superset_profile.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({
            "D": D,
            "circuits": {n: {k: v for k, v in p.items()
                             if k in ("widths", "D", "n_pi", "config", "bits", "offset")}
                         | {"skips": {f"{c},{d}": v for (c, d), v in p["skips"].items()}}
                         for n, p in prof.items()},
            "env_width": {str(k): v[0] for k, v in env_w.items()},
            "env_width_who": {str(k): v[1] for k, v in env_w.items()},
            "env_skip": {f"{c},{d}": v[0] for (c, d), v in env_s.items()},
            "env_skip_who": {f"{c},{d}": v[1] for (c, d), v in env_s.items()},
            "ff_max": ff_max[0], "pi_max": pi_max[0],
        }, f, ensure_ascii=False, indent=1)
    print(f"\n→ {out} に書き出した（Excel化と構造生成で使う）")


if __name__ == "__main__":
    main()
