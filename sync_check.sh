#!/bin/bash
# sync_check.sh — 実行マシン（iidalab など）で「git に対して何が足りない・何が変わったか」を点検し、
#                 足りないものだけを git から取ってくる。tgz を Downloads 経由で運ぶのをやめるためのもの（2026-09-08）。
#
#   ./sync_check.sh          点検だけ（何も変えない）
#   ./sync_check.sh --pull   点検して、遅れていれば git pull --ff-only（ローカル変更があれば止まる）
#
# 点検する項目
#   1. git: ブランチ / ローカルとリモート(origin/main)の差（遅れているコミット・変わるファイル）/ ローカルの未コミット変更
#   2. 環境: python3, ortools（配置配線に必要）, yosys（等価検証に必要。配置だけなら不要）
#   3. 生成物: 各作業に要るファイルが results/ にあるか。無ければ作るコマンドを示す
set -u
cd "$(dirname "$0")"
ROOT=$(pwd)
DO_PULL=0; [ "${1:-}" = "--pull" ] && DO_PULL=1
ok(){ printf "  ✅ %s\n" "$1"; }; ng(){ printf "  ❌ %s\n" "$1"; }; info(){ printf "  ・ %s\n" "$1"; }

echo "=== 1. git（$ROOT） ==="
BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || { ng "git リポジトリではない"; exit 1; }
git fetch -q origin 2>/dev/null || ng "git fetch 失敗（ネットワーク？）"
LOCAL=$(git rev-parse --short HEAD); REMOTE=$(git rev-parse --short origin/main 2>/dev/null || echo "?")
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
info "ブランチ $BR / ローカル $LOCAL / origin/main $REMOTE"
if [ "$BEHIND" = 0 ]; then ok "リモートと同じ（遅れ 0）"; else
  ng "リモートより $BEHIND コミット遅れ。取り込むと変わるファイル:"
  git diff --stat HEAD..origin/main | sed 's/^/      /' | tail -25
fi
[ "$AHEAD" != 0 ] && info "ローカルに未 push のコミットが $AHEAD 個ある"
MOD=$(git status --short | grep -v '^??' | wc -l); UNT=$(git status --short | grep '^??' | wc -l)
if [ "$MOD" = 0 ]; then ok "ローカルの未コミット変更なし"; else ng "ローカルに未コミット変更が $MOD 件（pull と衝突しうる）:"; git status --short | grep -v '^??' | sed 's/^/      /' | head -10; fi
[ "$UNT" != 0 ] && info "追跡外ファイル $UNT 件（生成物など。pull には影響しない）"

echo "=== 2. 環境 ==="
command -v python3 >/dev/null && ok "python3 $(python3 --version 2>&1 | cut -d' ' -f2)" || ng "python3 が無い"
if python3 -c "import ortools" 2>/dev/null; then ok "ortools（配置配線 OK）"; else ng "ortools が無い → source ~/venv_sopa/bin/activate（iidalab）または pip install ortools"; fi
YS=${YOSYS:-$(command -v yosys 2>/dev/null)}; if [ -n "$YS" ] && [ -x "$YS" ]; then ok "yosys: $YS"; else info "yosys 無し（配置配線だけなら不要。等価検証には YOSYS=/home/iidalab/oss-cad-suite/bin/yosys）"; fi
[ -d data/eblif_from_rtl ] && ok "data/eblif_from_rtl（41回路 eblif）$(ls data/eblif_from_rtl | wc -l) 回路" || ng "data/eblif_from_rtl が無い（git pull で入る）"
FREE=$(free -g 2>/dev/null | awk '/^Mem/{print $7}'); [ -n "$FREE" ] && info "空きメモリ ${FREE}GB → 配置の並列本数の目安 JOBS=$((FREE/2))"

echo "=== 3. 生成物（無いものは作るコマンドを示す） ==="
chk(){ # chk <説明> <パス> <作るコマンド>
  if [ -e "$2" ]; then ok "$1: $2"; else ng "$1: $2 が無い → $3"; fi; }
chk "skip有り超集合(D0=2)"   results/superset_d0_2.v   "D0=2 STEP=1 ./run_noskip_superset.sh; D0=2 STEP=2 ./run_noskip_superset.sh; D0=2 STEP=3 ./run_noskip_superset.sh"
chk "gap2まで中継(D0=3)"     results/superset_d0_3.v   "同上を D0=3 で"
chk "gap3まで中継(D0=4)"     results/superset_d0_4.v   "同上を D0=4 で"
chk "全部中継(D0=99)"        results/superset_noskip.v "STEP=1〜3 を D0 無しで"
chk "中継入り eblif (D0=3)"  results/eblif_relay_d0_3  "D0=3 STEP=1 ./run_noskip_superset.sh"
chk "中継入り eblif (D0=4)"  results/eblif_relay_d0_4  "D0=4 STEP=1 ./run_noskip_superset.sh"
chk "面積用 RTL (SoPA, 構成メモリ込み)" area/rtl/sopa_conf/superset_skip.v "./area/make_conf_rtl.sh（taurus2 向け。iidalab では不要）"
echo "     ※ 生成物は数秒〜数分（SATなし）。git には入れない（実行マシンで作る）"

if [ $DO_PULL = 1 ]; then
  echo "=== 4. pull ==="
  if [ "$BEHIND" = 0 ]; then ok "取り込むものなし"; elif [ "$MOD" != 0 ]; then ng "ローカル変更があるので pull しない。git stash か git checkout -- <file> で片付けてから"; exit 1;
  else git pull --ff-only origin main && ok "pull 完了 → $(git rev-parse --short HEAD)"; fi
else
  [ "$BEHIND" != 0 ] && echo "→ 取り込むには: ./sync_check.sh --pull"
fi
