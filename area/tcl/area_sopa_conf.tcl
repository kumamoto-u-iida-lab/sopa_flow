# ===============================================
# area_sopa_conf.tcl — SoPA 構造の面積を「構成メモリ（CONF_FF チェーン）込み」で測る（2026-10-06）
#   tcl/area_conf.tcl（9/8版）の kind=sopa_conf だけを抜き出した版。合成条件は area_conf.tcl と同一:
#     gscl45nm.db + dw_foundation.sldb、compile_ultra -no_autoungroup、report_area
#   ★追加点は1つ: report_area -hierarchy も出して、構成メモリ（CONF_TILE）とファブリック（FABRIC = cone）の
#     内訳を分けて読めるようにした。合成のやり方は変えていないので Total cell area は area_conf.tcl と同じ値になる。
#
# ■ 何が「config 込み」なのか
#   rtl/sopa_conf/<名前>.v は src/gen_conf_chain.py が作る。中身は
#     cone（配線構造そのもの。IMUX・PA・FLIPFLOP_NODE）
#     CONF_FF（1bit のシフトレジスタ。先輩の CONF_FF と同じ作り）
#     CONF_FF_TILE_N（CONF_FF を N 個直列。N = 構成メモリの bit 数）
#     SOPA_CORE（top。CONF_FF_TILE の CF[N-1:0] を cone の CONFIG_DATA に渡す）
#   top を SOPA_CORE にして合成するので、CONF_FF N 個ぶんの面積が Total cell area に入る。
#
# ■ 対象（N = 構成メモリ bit 数）
#   superset_mm20r2_alt_cyc   1,050PA / 20段 / N=14,695   small 41/41（段固定のみ）
#   superset_r1536_alt_cyc    1,536PA / 20段 / N=22,741   small 38/41（段固定）+ 3（案B・子ごと）
#   superset_allrelay_s125_alt_cyc  996PA / 18段 / N=15,189   比較用（9/23 から git 管理）
#
# ■ 使い方（taurus2。ログインシェルは tcsh なので `VAR=値 cmd` は通らない）
#   bash : CKT=superset_mm20r2_alt_cyc dc_shell -f ./tcl/area_sopa_conf.tcl
#   tcsh : ( setenv CKT superset_mm20r2_alt_cyc ; dc_shell -f ./tcl/area_sopa_conf.tcl )
#   まとめて: ./run_sopa_conf_new.sh（1プロセス1構造。前の構造の持ち越しを物理的に無くすため）
#   環境変数: CKT(必須) RTLDIR(既定 ./rtl) OUTDIR(既定 ./result_sopa_conf_fast) ALIB LIBDIR MAXCORES
#   結果: $OUTDIR/<CKT>.rep の "Total cell area"、内訳は $OUTDIR/<CKT>_hier.rep
# ===============================================

proc envget {name dflt} {
    global env
    if {[info exists env($name)] && [string length $env($name)] > 0} { return $env($name) }
    return $dflt
}

set ckt        [envget CKT    ""]
set rtldir     [envget RTLDIR "./rtl"]
set output_dir [envget OUTDIR "./result_sopa_conf_fast"]
if {$ckt eq ""} {
    echo "ERROR: CKT を環境変数で渡すこと（例: CKT=superset_mm20r2_alt_cyc dc_shell -f ./tcl/area_sopa_conf.tcl）"
    quit
}
file mkdir $output_dir

set my_toplevel      SOPA_CORE
set my_verilog_files [list $rtldir/sopa_conf/$ckt.v]
if {![file exists [lindex $my_verilog_files 0]]} {
    echo "ERROR: RTL が無い: [lindex $my_verilog_files 0]"
    quit
}

# ---- レジューム: Total cell area まで出ている .rep があればスキップ（途中で kill した空ファイルは測り直す） ----
set rep_name  "$output_dir/$ckt.rep"
set hier_name "$output_dir/${ckt}_hier.rep"
if {[file exists $rep_name]} {
    set fh [open $rep_name r]; set body [read $fh]; close $fh
    if {[string first "Total cell area" $body] >= 0} { echo "== SKIP $ckt（$rep_name が完成済み）"; quit }
    file delete $rep_name
}

# ---- ライブラリ（area_conf.tcl と同一。ここは触らない） ----
set OSU_FREEPDK "/opt/EDA/LIB/FreePDK45/osu_soc/lib/files"
set search_path [concat $search_path $OSU_FREEPDK [list [envget LIBDIR "."]]]
set link_library [set target_library [concat [list gscl45nm.db] [list dw_foundation.sldb]]]
set target_library "gscl45nm.db"
set alib_library_analysis_path [envget ALIB "./alib"]
set_svf -off
suppress_message OPT-314
suppress_message OPT-150

echo "== START $ckt  top=$my_toplevel"
set t0 [clock seconds]
analyze -f verilog $my_verilog_files
set t_ana [clock seconds]
elaborate $my_toplevel
current_design $my_toplevel
set t_ela [clock seconds]

# ---- 合成（area_conf.tcl と同一。ここを変えると面積が変わる） ----
set maxcores [envget MAXCORES ""]
if {$maxcores ne ""} { set_host_options -max_cores $maxcores }
compile_ultra -no_autoungroup
check_design
set t_cmp [clock seconds]

# ---- レポート ----
report_area > $rep_name
report_area -hierarchy > $hier_name
report_area
set t_rep [clock seconds]

set dt [expr {$t_rep - $t0}]
echo "== DONE $ckt ${dt}s"
set fh [open "$output_dir/timing.log" a]; puts $fh "$ckt\t$dt"; close $fh
set fh [open "$output_dir/steps.log" a]
puts $fh [format "%s\ttotal=%d\tanalyze=%d\telaborate=%d\tcompile=%d\treport=%d" \
    $ckt $dt [expr {$t_ana - $t0}] [expr {$t_ela - $t_ana}] [expr {$t_cmp - $t_ela}] [expr {$t_rep - $t_cmp}]]
close $fh
quit
