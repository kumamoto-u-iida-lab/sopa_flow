# area/ — 構成メモリ込みの面積測定（2026-09-08）

先生 9/4 の指摘「島は構成メモリ込み、SoPA/IPGen は抜き」を揃えるための一式。**このリポジトリだけで完結**する。
先輩の CONF_FF / CONF_FF_TILE_N / FPGA_CORE と同じ作りのスキャンチェーン（CONF_CLK, CONF_RESETL, CONF_MODE, CONF_IN, CONF_E, CONF_OUT）を
各構造に付け、その CF を CONFIG_DATA に渡す。

## 手順
```bash
./area/make_conf_rtl.sh          # ① SoPA 側 RTL を生成（D0=2/3/4/99 → area/rtl/sopa_conf/*.v、数分、SATなし）
# ② area/ を taurus2 へ。gscl45nm.db / dw_foundation.sldb / .synopsys_dc.setup を area/ 直下に置く（9/1 の run_parallel.sh と同じ）
cd area && JOBS=1 ./run_conf.sh |& tee run_conf.log     # ③ 1プロセス1構造で 5本
```
| 対象 | top | bit | ファイル |
|---|---|---|---|
| SoPA skip有り超集合 | SOPA_CORE | 10,350 | rtl/sopa_conf/superset_skip.v（生成物、git 管理外） |
| SoPA gap2まで中継 | SOPA_CORE | 10,580 | rtl/sopa_conf/superset_d0_3.v |
| SoPA gap3まで中継 | SOPA_CORE | 11,353 | rtl/sopa_conf/superset_d0_4.v |
| SoPA 全部中継 | SOPA_CORE | 11,083 | rtl/sopa_conf/superset_noskip.v |
| ★SoPA 全部中継・交互(alt_cyc) 37/41 | SOPA_CORE | 11,083 | rtl/sopa_conf/superset_allrelay_alt_cyc.v（git 管理、9/23） |
| ★SoPA 列数1.25倍・交互(alt_cyc) 41/41 | SOPA_CORE | 15,189 | rtl/sopa_conf/superset_allrelay_s125_alt_cyc.v（git 管理、9/23） |
| ~~SoPA 余りの割合をそろえた20段・交互 41/41~~ ※16→7 が2倍超で規則違反（段18の行14・15が死んだPA）→ mm20r2 に置き換え | SOPA_CORE | 14,695 | rtl/sopa_conf/superset_mm20ff7_alt_cyc.v（10/4、使わない） |
| ★SoPA 1,050PA 余りの割合をそろえた配分・隣2倍以内・交互 41/41（段固定のみ） | SOPA_CORE | 14,695 | rtl/sopa_conf/superset_mm20r2_alt_cyc.v（git 管理、10/6） |
| ★SoPA 1,536PA 規則（FF側7から倍々＋入力側等比）・交互 38/41＋案B救済3 | SOPA_CORE | 22,741 | rtl/sopa_conf/superset_r1536_alt_cyc.v（git 管理、10/6） |
| ★SoPA 1,536PA 外部入力を FF 側ほど減らした入れ子（45/36/24/12本）・交互 38/41 | SOPA_CORE | 21,065 | rtl/sopa_conf/superset_r1536_alt_cyc_ext45n.v（git 管理、10/14） |
| ★SoPA 1,536PA PI ノード（段0=EXT 45本を1対1直結の45列、段1以降の IMUX に EXT 無し）・交互 40/41（e4 未決着） | SOPA_CORE | 17,975 | rtl/sopa_conf/superset_r1536pi_alt_cyc.v（git 管理、10/14） |
| ★SoPA 1,536PA PI ノード・FF 側 28/14/7 列（隣2倍以内）・交互 40/41（e4 案B 実行中） | SOPA_CORE | 17,699 | rtl/sopa_conf/superset_r1536pi_ff7_alt_cyc.v（git 管理、10/15） |
| SoPA 全部中継・巡回(cyclic_eq) | SOPA_CORE | 11,083 | rtl/sopa_conf/superset_allrelay_cyclic_eq.v（★git 管理、9/17） |
| IPGen 超集合 x11_y17_om19_pi45 | FPGA_CORE | 10,184 | rtl/ipgen_conf/superset/（EFPGA_CORE 一式 + FPGA_CORE_conf.v、git 管理） |

- `tcl/area_conf.tcl` = 9/1 の area_one.tcl に kind `sopa_conf` / `ipgen_conf` を足しただけ（合成条件は同一: gscl45nm, compile_ultra -no_autoungroup, report_area）
- 結果: `result_sopa_conf_fast/<名前>.rep`, `result_ipgen_conf_fast/superset.rep`。`Total cell area` を見る
- 島（6x6 W32 fc32 = 846,225 μm²）は元から CONF_FF 込みなので測り直し不要
- 9/1 の構成メモリ抜きの値: SoPA 379,783 / IPGen 676,763 μm²。CONF_FF 1個 ≈ 20.6 μm²（6月の島レポート）なので
  込みの見込みは SoPA ≈ 593k / IPGen ≈ 887k / 島 846k（推測）

## 2026-10-06 追加: tcl/area_sopa_conf.tcl と run_sopa_conf_new.sh
area_conf.tcl の kind=sopa_conf だけを抜き出し、`report_area -hierarchy` を足した版（合成条件は同一）。
構成メモリ（CONF_TILE）と配線構造（FABRIC = cone）の面積を分けて読める。
```bash
cd area && JOBS=1 ./run_sopa_conf_new.sh |& tee run_sopa_conf_new.log   # mm20r2 / r1536 / s125_alt_cyc の3本
```
結果: result_sopa_conf_fast/<名前>.rep（Total cell area）、<名前>_hier.rep（内訳）。

## 2026-10-17 追加: ff7 の作り方のまま大きさを振った7構造（superset_pi_ff7_s*_alt_cyc）
包絡線（PI ノード込み41回路の行ごとの最大、計1,216PA）× 倍率。行0(FF)=7・最上段=45 固定、他は ⌈包絡線×倍率⌉、入力側の行 ≤ 2×FF側の隣。
1.263倍は ff7（superset_r1536pi_ff7_alt_cyc、測定済みなら不要）。配置は ../run_sweep_ff7.sh（iidalab）。
| 名前 | 倍率 | PA | bit |
|---|---|---|---|
| superset_pi_ff7_s100_alt_cyc | 1.00 | 1,218 | 13,547 |
| superset_pi_ff7_s105_alt_cyc | 1.05 | 1,288 | 14,489 |
| superset_pi_ff7_s110_alt_cyc | 1.10 | 1,345 | 15,239 |
| superset_pi_ff7_s115_alt_cyc | 1.15 | 1,402 | 15,991 |
| superset_pi_ff7_s120_alt_cyc | 1.20 | 1,456 | 16,645 |
| （ff7 superset_r1536pi_ff7_alt_cyc） | 1.263 | 1,536 | 17,699 |
| superset_pi_ff7_s135_alt_cyc | 1.35 | 1,626 | 18,839 |
| superset_pi_ff7_s150_alt_cyc | 1.50 | 1,784 | 20,831 |
```bash
cd area && JOBS=1 TARGETS="superset_pi_ff7_s100_alt_cyc superset_pi_ff7_s105_alt_cyc superset_pi_ff7_s110_alt_cyc superset_pi_ff7_s115_alt_cyc superset_pi_ff7_s120_alt_cyc superset_pi_ff7_s135_alt_cyc superset_pi_ff7_s150_alt_cyc" ./run_sopa_conf_new.sh |& tee run_sweep_ff7_area.log
```

## 2026-10-20 追加: 外部入力を論理の1つ上で受ける構造（superset_pilocal_s120_alt_cyc）
PI ノードを回路ごとに論理の一番上の行の1つ上に置き、行1〜17 の ia に専用の EXT[j mod 45] を1本足した構造（structures/README.md）。
包絡線 1,072 ×1.2 = 1,289PA、14,917bit、19段、EXT 45本。見積もり 479,500〜491,700 μm²（bit／IMUX 入力の直線、推測）。
```bash
cd area && JOBS=1 TARGETS="superset_pilocal_s120_alt_cyc" ./run_sopa_conf_new.sh |& tee run_pilocal_area.log
```

## 2026-10-21 追加: EXT を受ける列を絞った r1536（superset_r1536_xc_{head,tail,even,reach2}_alt_cyc）
比較の相手は PA 1,536 の r1536（1,100,898）/ ext45n（871,531）/ ff7（568,105）。見積もり 約 677,000 μm²（推測）。
```bash
cd area && JOBS=1 TARGETS="superset_r1536_xc_even_alt_cyc superset_r1536_xc_reach2_alt_cyc superset_r1536_xc_tail_alt_cyc superset_r1536_xc_head_alt_cyc" ./run_sopa_conf_new.sh |& tee run_xc_area.log
```

## 2026-10-22 追加: pilocal を PA 数 1,152/1,536/1,920/2,304/3,072 で（superset_pilocal_pa<N>_alt_cyc）
```bash
cd area && JOBS=1 TARGETS="superset_pilocal_pa1152_alt_cyc superset_pilocal_pa1536_alt_cyc superset_pilocal_pa1920_alt_cyc superset_pilocal_pa2304_alt_cyc superset_pilocal_pa3072_alt_cyc" ./run_sopa_conf_new.sh |& tee run_pilocal_sweep_area.log
```
