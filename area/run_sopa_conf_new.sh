#!/bin/bash
# run_sopa_conf_new.sh — 構成メモリ込みの SoPA 面積を、1プロセス1構造で測る（taurus2、2026-10-06）
#   使い方: cd area && JOBS=1 ./run_sopa_conf_new.sh |& tee run_sopa_conf_new.log
#   ライブラリ(gscl45nm.db / dw_foundation.sldb / .synopsys_dc.setup)は area/ 直下に置く（run_conf.sh と同じ）。
set -u
cd "$(dirname "$0")"; ROOT=$(pwd)
JOBS="${JOBS:-1}"
TARGETS="${TARGETS:-superset_mm20r2_alt_cyc superset_r1536_alt_cyc superset_allrelay_s125_alt_cyc}"
mkdir -p logs run alib result_sopa_conf_fast
run_one() {
  local ckt="$1" d="run/sopa_conf_$1"; mkdir -p "$d"
  for f in "$ROOT"/*.db "$ROOT"/*.sldb "$ROOT"/.synopsys_dc.setup; do [ -e "$f" ] && ln -sfn "$f" "$d/" 2>/dev/null; done
  ( cd "$d" && env CKT="$ckt" RTLDIR="$ROOT/rtl" OUTDIR="$ROOT/result_sopa_conf_fast" ALIB="$ROOT/alib" LIBDIR="$ROOT" \
      dc_shell -f "$ROOT/tcl/area_sopa_conf.tcl" ) > "logs/sopa_conf_${ckt}.log" 2>&1
  echo "   終了: $ckt (rc=$?)  $(grep -m1 'Total cell area' result_sopa_conf_fast/${ckt}.rep 2>/dev/null)"
}
export -f run_one; export ROOT
for c in $TARGETS; do echo "$c"; done | xargs -P "$JOBS" -L1 bash -c 'run_one $0'
echo "=== 結果（Total cell area） ==="; for c in $TARGETS; do printf '%-34s %s\n' "$c" "$(grep -m1 'Total cell area' result_sopa_conf_fast/$c.rep 2>/dev/null | awk '{print $NF}')"; done
echo "=== 内訳（report_area -hierarchy の CONF_TILE = 構成メモリ / FABRIC = 配線構造） ==="; for c in $TARGETS; do echo "$c"; grep -E "^(CONF_TILE|FABRIC) " result_sopa_conf_fast/${c}_hier.rep 2>/dev/null | sed "s/^/   /"; done
