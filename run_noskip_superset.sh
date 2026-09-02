#!/bin/bash
# run_noskip_superset.sh — 「skip配線を一切持たないスーパーセット構造」に41回路が載るかを一気に試す。
#
#   2026-09-02 作成。段飛び辺をすべて中継(フィードスルー=素通しのPA)で運ぶ。
#   段固定では中継の段と個数が確定するので、ネットリスト側にセルを足すだけで済み、
#   配置配線は「行だけ解く」既存の段固定ツール(place_fixed_skip_ext.py)がそのまま使える。
#
#   手順  ① insert_relay.py         41回路の eblif に中継セルを挿入        (SATなし・数秒)
#         ② gen_ext_uniform_all.py  回路ごとの skip無し構造(幅を数えるため) (SATなし・数秒)
#         ③ superset_profile.py     FF側で揃えて段別 max → 包絡線 json      (SATなし)
#            gen_superset.py        包絡線から superset.v を生成
#         ④ place_fixed_skip_ext.py 41回路を superset.v に段固定で配置配線  (★ここだけSAT)
#
#   使い方:  JOBS=4 ATIME=1800 ./run_noskip_superset.sh            # 全部
#            STEP=4 JOBS=4 ATIME=3600 ./run_noskip_superset.sh e4 e2  # ④だけ・回路を絞る
#   環境変数: JOBS(並列本数, 既定2) / ATIME(1回路のSAT上限秒, 既定1800) / STEP(この番号の手順だけ)
#             TOOL(④の配置ツール, 既定 place_fixed_skip_ext.py。place_fixed_tbl.py=表制約版、難物に速い)
#   出力:   results/eblif_relay/ results/cone_noskip/ results/superset_profile.json results/superset_noskip.v
#           results/noskip_place/<回路>.log  と  results/noskip_place/summary.csv
#   ※ 並列本数の目安: 空きメモリ(GB) ÷ 2
set -u
ROOT=$(cd "$(dirname "$0")" && pwd)
SRC=$ROOT/src
RES=$ROOT/results
JOBS=${JOBS:-2}
ATIME=${ATIME:-1800}
STEP=${STEP:-all}
TOOL=${TOOL:-place_fixed_skip_ext.py}
mkdir -p "$RES" "$RES/noskip_place"

if [ "$STEP" = all ] || [ "$STEP" = 1 ]; then
  echo "=== ① 中継挿入 ==="
  (cd "$SRC" && python3 insert_relay.py) || exit 1
fi
if [ "$STEP" = all ] || [ "$STEP" = 2 ]; then
  echo "=== ② 回路ごとの skip無し構造（幅を数えるため） ==="
  (cd "$SRC" && EBDIR="$RES/eblif_relay" OUTDIR="$RES/cone_noskip" SKIP_SPECS=2:0 python3 gen_ext_uniform_all.py) || exit 1
fi
if [ "$STEP" = all ] || [ "$STEP" = 3 ]; then
  echo "=== ③ 包絡線 → スーパーセット構造 ==="
  (cd "$SRC" && SRC="$RES/cone_noskip" python3 superset_profile.py) || exit 1
  (cd "$SRC" && PROFILE="$RES/superset_profile.json" OUT="$RES/superset_noskip.v" TAG=superset_noskip python3 gen_superset.py) || exit 1
fi
if [ "$STEP" = all ] || [ "$STEP" = 4 ]; then
  echo "=== ④ 41回路をスーパーセットに段固定配置 (JOBS=$JOBS ATIME=$ATIME TOOL=$TOOL) ==="
  CONE=$RES/superset_noskip.v
  [ -f "$CONE" ] || { echo "$CONE が無い。STEP=3 を先に"; exit 1; }
  if [ $# -gt 0 ]; then CKTS="$*"; else CKTS=$(ls "$RES/eblif_relay"); fi
  one() {
    c=$1
    (cd "$SRC" && ATIME=$ATIME python3 "$TOOL" "$RES/eblif_relay/$c/mapped_$c.v.eblif" "$CONE") > "$RES/noskip_place/$c.log" 2>&1
    r=$(grep -m1 "^結果:" "$RES/noskip_place/$c.log" | sed 's/^結果: //')
    echo "$c  $r"
  }
  export -f one; export SRC RES ATIME CONE TOOL
  echo "$CKTS" | tr ' ' '\n' | xargs -P "$JOBS" -I{} bash -c 'one {}'
  echo "circuit,result" > "$RES/noskip_place/summary.csv"
  for c in $CKTS; do
    r=$(grep -m1 "^結果:" "$RES/noskip_place/$c.log" | sed 's/^結果: //' | cut -d' ' -f1)
    echo "$c,$r" >> "$RES/noskip_place/summary.csv"
  done
  echo; echo "=== 集計 ==="; cut -d, -f2 "$RES/noskip_place/summary.csv" | tail -n +2 | sort | uniq -c
fi
