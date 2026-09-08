#!/bin/bash
# make_conf_rtl.sh — SoPA 側の「構成メモリ込み」RTL を、このリポジトリだけで作り直す（2026-09-08）
#   ① run_noskip_superset.sh の手順①〜③（SATなし）で超集合構造を D0 ごとに生成
#        D0=2  skip有り超集合（中継なし = 8/31 の superset.v と同じ 10,350bit）
#        D0=3  gap2 まで中継 / D0=4 gap3 まで中継 / D0=99 全部中継
#   ② gen_conf_chain.py で CONF_FF チェーン + SOPA_CORE を付けて area/rtl/sopa_conf/ に置く
#   使い方: ./area/make_conf_rtl.sh            （D0S="2 3 4 99" が既定）
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
D0S="${D0S:-2 3 4 99}"
mkdir -p "$ROOT/area/rtl/sopa_conf"
for d in $D0S; do
  echo "=== D0=$d: 構造生成（①〜③） ==="
  for s in 1 2 3; do D0=$d STEP=$s "$ROOT/run_noskip_superset.sh" > /dev/null || { echo "STEP=$s 失敗 (D0=$d)"; exit 1; }; done
  if [ "$d" = 99 ]; then src="$ROOT/results/superset_noskip.v"; name=superset_noskip; else src="$ROOT/results/superset_d0_$d.v"; name=superset_d0_$d; fi
  [ "$d" = 2 ] && name=superset_skip
  python3 "$ROOT/src/gen_conf_chain.py" "$src" "$ROOT/area/rtl/sopa_conf/$name.v"
  head -1 "$src" | grep -o "CONFIG=[0-9]*bit"
done
ls -la "$ROOT/area/rtl/sopa_conf/"
