# ★area_conf.tcl = area_one.tcl（9/1版）に kind sopa_conf / ipgen_conf を足しただけ。合成条件は無変更（2026-09-08）
# ===============================================
# セル面積の解析 — 1プロセス1回路版 (A1〜A4)
#   2026-08-30 作成。tcl/ipgen_area.tcl と tcl/sopa_area.tcl は無改変で温存する。
#
# ■ なぜ作ったか
#   ① e4(IPGen) が旧TCLでは 2時間48分たっても Total cell area を出さなかった。
#      止まっていたのは compile ではなく【report_area】。
#      2026-08-30 taurus2 で追試: compile 完了 18:12:53 → 2時間たっても report_area のまま。
#      → DISABLE_LOOPS=1 （compile後に set_disable_timing）で回避する。下の該当箇所を見ること。
#   ② girl10 → cat と同じセッションで続けて回すと cat の結果が変わった。
#      部品の個数は完全に同一(IMUX_IN063=128, OMUX_IN024=30, PAE=40 …)で、
#      違いは buf/inv 3293 → 2425、面積 42265.63 vs 40103.56。
#      ★2026-08-30 決着: 1プロセス1回路のクリーン実行で cat = 40103.561777。
#        つまり【旧TCLの 42265.63 が異常値】で、set_disable_timing は無罪だった。
#        真因(remove_design -all を打っているのに何が残るのか)は未特定。
#        → 追わずに「1プロセスで1回路だけ」にして持ち越しを物理的に無くす方針。
#
# ■ 旧TCLとの差分 (A1〜A4)
#   A1 回路ループを廃止。回路は環境変数 CKT で1つだけ受け取る。
#      → 並列実行できる／前の回路の持ち越しが起こりえない
#   A2 レポートは report_area だけにした。
#      旧: report_area / report_reference -hierarchy / report_resource /
#          report_design / report_hierarchy / report_area -hierarchy / link
#      ※ REPORTS=full を付ければ旧と同じ6種類を出す(解析用に残してある)
#   A3 write -f verilog -hierarchy と write -f ddc をやめた。面積の算出に不要。
#   A4 suppress_message OPT-314 OPT-150。旧の e4.rep は 5.6MB が全部この警告だった。
#
#   おまけ1: glob の結果を lsort して読み込み順を固定した(実行ごとのブレを1つ消す)
#   おまけ2: analyze / elaborate / compile / report の所要秒数を別々に記録する
#            → 「どこが遅いのか」がこれで初めて分かる
#
# ■ ★面積の値に効く部分は一切変えていない
#   ライブラリ設定 / analyze / elaborate / compile_ultra -no_autoungroup / check_design
#   → 値が 8/25 の旧TCLと一致するかを girl10 と cat で必ず照合すること:
#        girl10  SoPA  7321.079865   IPGen 13180.290339
#        cat     SoPA 26362.927076   IPGen 42265.626788
#
# ■ 使い方
#   単体(bash):  CKT=girl10 KIND=ipgen dc_shell -f ./tcl/area_one.tcl
#   単体(tcsh):  ( setenv KIND ipgen ; setenv CKT girl10 ; dc_shell -f ./tcl/area_one.tcl ) &
#                ★taurus2 のログインシェルは tcsh。`VAR=値 cmd` は通らない
#   e4 は DISABLE_LOOPS=1 が必須（付けないと report_area で戻ってこない）
#   並列:  ../run_parallel.sh          ← こちらを推奨
#   環境変数: CKT(必須) KIND(必須 sopa|ipgen) OUTDIR REPORTS(min|full) RTLDIR ALIB
# ===============================================

proc envget {name dflt} {
    global env
    if {[info exists env($name)] && [string length $env($name)] > 0} {
        return $env($name)
    }
    return $dflt
}

set ckt     [envget CKT     ""]
set kind    [envget KIND    ""]
set reports [envget REPORTS "min"]
set rtldir  [envget RTLDIR  "./rtl"]

if {$ckt eq "" || $kind eq ""} {
    echo "ERROR: CKT と KIND を環境変数で渡すこと"
    echo "  例: CKT=girl10 KIND=ipgen dc_shell -f ./tcl/area_one.tcl"
    quit
}

set output_dir [envget OUTDIR "./result_${kind}_fast"]
file mkdir $output_dir

# ---- 回路の種類ごとの設定（トップ名と入力ファイル） ----
if {$kind eq "sopa"} {
    set my_toplevel      cone
    set my_verilog_files [list $rtldir/sopa/$ckt.v]
} elseif {$kind eq "ipgen"} {
    set my_toplevel      EFPGA
    # ★lsort で読み込み順を固定する（旧TCLは glob の生の順だった）
    set my_verilog_files [lsort [concat \
        [glob -nocomplain "$rtldir/ipgen/$ckt/*.v"] \
        [glob -nocomplain "$rtldir/ipgen/$ckt/*/*.v"]]]
} elseif {$kind eq "sopa_conf"} {
    # ★2026-09-08: 構成メモリ(CONF_FF チェーン)込み。top=SOPA_CORE（gen_conf_chain.py が付けたラッパ）
    set my_toplevel      SOPA_CORE
    set my_verilog_files [list $rtldir/sopa_conf/$ckt.v]
} elseif {$kind eq "ipgen_conf"} {
    # ★2026-09-08: 構成メモリ込み。top=FPGA_CORE（先輩の FPGA_CORE.v と同じ形のラッパ + EFPGA_CORE の全 .v）
    set my_toplevel      FPGA_CORE
    set my_verilog_files [lsort [concat         [glob -nocomplain "$rtldir/ipgen_conf/$ckt/*.v"]         [glob -nocomplain "$rtldir/ipgen_conf/$ckt/*/*.v"]]]
} else {
    echo "ERROR: KIND は sopa / ipgen / sopa_conf / ipgen_conf のどれか（今の値: $kind）"
    quit
}

if {[llength $my_verilog_files] == 0} {
    echo "ERROR: RTLが見つからない  kind=$kind ckt=$ckt rtldir=$rtldir"
    quit
}

# ---- レジューム: 既に測ってあればスキップ ----
#   ★2026-08-30 修正: 「ファイルがあるか」で判定していたら、途中でkillした実行が
#     残した空の .rep をスキップしてしまった。`report_area > $rep_name` の
#     リダイレクトはコマンドが戻る前にファイルを作るため。
#     → 中身に "Total cell area" があるかで判定する。
set rep_name [format "%s/%s%s" $output_dir $ckt ".rep"]
if {[file exists $rep_name]} {
    set done 0
    if {[catch {
        set fh [open $rep_name r]
        set body [read $fh]
        close $fh
        if {[string first "Total cell area" $body] >= 0} { set done 1 }
    } err]} {
        echo "== 警告: $rep_name を読めなかった（$err）。測り直す。"
    }
    if {$done} {
        echo "== SKIP  $kind/$ckt  （$rep_name が完成済み）"
        quit
    }
    echo "== 前回の中途半端な $rep_name を捨てて測り直す"
    file delete $rep_name
}

# ---- ライブラリの設定（旧TCLと同一。ここは触らない） ----
set OSU_FREEPDK "/opt/EDA/LIB/FreePDK45/osu_soc/lib/files"
# ★LIBDIR: run/ の下で走らせるので、作業ルートも search_path に足す。
#   8/25 の実行では gscl45nm.db が作業ディレクトリ直下から読まれていた
#   （レポートの "File: .../SoPA_8_25_area/gscl45nm.db"）。これを見失わないため。
set search_path [concat  $search_path $OSU_FREEPDK [list [envget LIBDIR "."]]]
set link_library [set target_library [concat  [list gscl45nm.db] [list dw_foundation.sldb]]]
set target_library "gscl45nm.db"

# ---- 並列実行のための後始末（プロセス同士がファイルを取り合わないように） ----
# alib(セルの事前解析キャッシュ)は全プロセスで同じ場所を共有する。
# 空だと各プロセスが同時に作りにいって競合するので、
# run_parallel.sh が先に1本だけ流して作ってから並列に入る。
set alib_library_analysis_path [envget ALIB "./alib"]
# SVF(Formality用の記録)は面積測定に不要。プロセス間で default.svf を取り合うのも防ぐ。
set_svf -off

# ---- A4: 警告の印字を止める ----
#   OPT-150 = タイミングループを検出した / OPT-314 = ループを切るためにアークを無効化した
#   ★これは「印字を止める」だけで、合成のやり方は一切変えない。
#     （noloop版でやった set_disable_timing とは別物）
suppress_message OPT-314
suppress_message OPT-150

echo "== START $kind/$ckt   files=[llength $my_verilog_files]"
set t0 [clock seconds]

# ---- 解析と展開（旧TCLと同一） ----
analyze -f verilog $my_verilog_files
set t_ana [clock seconds]

elaborate $my_toplevel
current_design $my_toplevel
set t_ela [clock seconds]

# ---- 合成（旧TCLと同一。ここを変えると面積が変わる） ----
# A5: MAXCORES を渡すとマルチコアで合成する（既定は使わない=旧TCLと同じ）。
#   時間の96%は compile なので、削るならここしかない（girl10 taurus2 実測: total 68s / compile 65s）。
#   ★面積の値は変わらない「はず」。girl10 で 13180.290339 のままかを必ず確認すること。
set maxcores [envget MAXCORES ""]
if {$maxcores ne ""} {
    echo "== マルチコア: max_cores $maxcores"
    set_host_options -max_cores $maxcores
}
compile_ultra -no_autoungroup
check_design
set t_cmp [clock seconds]

# ---- ★DISABLE_LOOPS: report の前にタイミングループの通り道を無効化する ----
#   なぜ要るか: e4(IPGen) は compile が終わった後の report_area が戻ってこない。
#     2026-08-30 taurus2 実測 = compile 完了 18:12:53 → 2時間たっても report_area のまま。
#     2026-08-25 の旧TCLでも 2時間48分で未完了。noloop版(この処理あり)は 1599秒で完走。
#   値を変えないことの根拠(2026-08-30):
#     girl10 この処理あり/なし = 13180.290339 で一致
#     cat    この処理あり = 40103.561777 、1プロセス1回路のクリーン実行も 40103.561777 で一致
#     （8/25 旧TCL の cat 42265.63 の方が、セッション持ち越しによる異常値だった）
#   ★compile の後に打つので、合成のやり方は変えない。タイミング計算の経路を切るだけ。
if {[envget DISABLE_LOOPS "0"] ne "0" && $kind eq "ipgen"} {
    echo "== タイミングループの通り道を無効化する"
    set t_dis0 [clock seconds]

    # ① OMUX の放送経路: PAE出力(FF未通過) → OMUX → 他レーンのIMUX → PAE → …
    #    レーンは前方向にしか直結していないので、ループは必ず OMUX を通る
    set omux_cells [get_cells -hier -filter "ref_name =~ OMUX_IN*"]
    echo "   OMUX: [sizeof_collection $omux_cells] 個"
    if {[sizeof_collection $omux_cells] > 0} { set_disable_timing $omux_cells }

    # ② PAE 内部のフィードバック: mode[6][7] で O_A↔O_B の向きを切り替えている
    #    ★DCが階層をユニーク化して PAE → PAE_0..PAE_N になるので PAE_* で拾い、
    #      PAE_BUNDLE_* は除く（BUNDLEごと切ると IMUX まで巻き込む）
    set pae_all   [get_cells -hier -filter "ref_name =~ PAE_*"]
    set pae_bnd   [get_cells -hier -filter "ref_name =~ PAE_BUNDLE_*"]
    set pae_cells [remove_from_collection $pae_all $pae_bnd]
    echo "   PAE : [sizeof_collection $pae_cells] 個 （BUNDLE [sizeof_collection $pae_bnd] 個は除外）"
    if {[sizeof_collection $pae_cells] > 0} { set_disable_timing $pae_cells }

    echo "== 無効化にかかった時間 [expr {[clock seconds] - $t_dis0}]s"
}
# ※ SoPA側(kind=sopa)には入れていない。8/25 に e4 まで素で完走しているので不要。
#    必要になったら、SoPA のどのセルがループを作るかを確かめてから足すこと。

# ---- A2: レポート ----
report_area > $rep_name
if {$reports eq "full"} {
    # 旧TCLと同じ内容（部品ごとの内訳を見たいときだけ）
    report_reference -hierarchy >> $rep_name
    report_resource             >> $rep_name
    report_design               >> $rep_name
    report_hierarchy            >> $rep_name
    report_area -hierarchy      >> $rep_name
    link                        >> $rep_name
}
report_area
set t_rep [clock seconds]

# ---- A3: write はしない ----
#   旧TCL: write -f verilog -hierarchy / write -f ddc
#   面積の算出に不要。ネットリストが要るときだけ REPORTS=full とは別に手で足すこと。

# ---- 記録 ----
set dt [expr {$t_rep - $t0}]
echo "== DONE  $kind/$ckt  ${dt}s"

# timing.log は旧フォーマット（回路名 TAB 秒）のまま。collect_area.py がこれを読む。
set fh [open "$output_dir/timing.log" a]
puts $fh "$ckt\t$dt"
close $fh

# steps.log に内訳を残す。「どこが遅いか」はこれを見る。
set fh [open "$output_dir/steps.log" a]
puts $fh [format "%s\ttotal=%d\tanalyze=%d\telaborate=%d\tcompile=%d\treport=%d" \
    $ckt $dt [expr {$t_ana - $t0}] [expr {$t_ela - $t_ana}] \
    [expr {$t_cmp - $t_ela}] [expr {$t_rep - $t_cmp}]]
close $fh

quit
