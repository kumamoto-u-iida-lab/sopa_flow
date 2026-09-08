#!/bin/bash
# run_conf.sh — 構成メモリ込みの面積測定（taurus2）。9/1 の run_parallel.sh と同じ流儀で 1プロセス1構造。
#   使い方: cd area_conf_pkg && JOBS=1 ./run_conf.sh
#   対象: sopa_conf × {superset_skip superset_noskip superset_d0_3 superset_d0_4} / ipgen_conf × superset
#   ライブラリ(gscl45nm.db 等)は 9/1 と同じく作業ルートに置く（run_parallel.sh と同じ）。IPGen は DISABLE_LOOPS=1。
set -u
cd "$(dirname "$0")"; ROOT=$(pwd)
JOBS="${JOBS:-1}"
SOPA="${SOPA:-superset_skip superset_noskip superset_d0_3 superset_d0_4}"
mkdir -p logs run alib result_sopa_conf_fast result_ipgen_conf_fast
run_one() {
  local kind="$1" ckt="$2" d="run/${kind}_${ckt}"; mkdir -p "$d"
  for f in "$ROOT"/*.db "$ROOT"/*.sldb "$ROOT"/.synopsys_dc.setup; do [ -e "$f" ] && ln -sfn "$f" "$d/" 2>/dev/null; done
  local extra=""; [ "$kind" = ipgen_conf ] && extra="DISABLE_LOOPS=1"
  ( cd "$d" && env $extra CKT="$ckt" KIND="$kind" REPORTS=min RTLDIR="$ROOT/rtl" OUTDIR="$ROOT/result_${kind}_fast" ALIB="$ROOT/alib" LIBDIR="$ROOT" \
      dc_shell -f "$ROOT/tcl/area_conf.tcl" ) > "logs/${kind}_${ckt}.log" 2>&1
  echo "   終了: ${kind}/${ckt} (rc=$?)  $(grep -m1 'Total cell area' result_${kind}_fast/${ckt}.rep 2>/dev/null)"
}
export -f run_one; export ROOT
{ for c in $SOPA; do echo "sopa_conf $c"; done; echo "ipgen_conf superset"; } | xargs -P "$JOBS" -L1 bash -c 'run_one $0 $1'
echo "=== 結果 ==="; grep -H "Total cell area" result_*_conf_fast/*.rep
