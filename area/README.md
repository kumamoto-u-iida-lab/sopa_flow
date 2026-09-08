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
| IPGen 超集合 x11_y17_om19_pi45 | FPGA_CORE | 10,184 | rtl/ipgen_conf/superset/（EFPGA_CORE 一式 + FPGA_CORE_conf.v、git 管理） |

- `tcl/area_conf.tcl` = 9/1 の area_one.tcl に kind `sopa_conf` / `ipgen_conf` を足しただけ（合成条件は同一: gscl45nm, compile_ultra -no_autoungroup, report_area）
- 結果: `result_sopa_conf_fast/<名前>.rep`, `result_ipgen_conf_fast/superset.rep`。`Total cell area` を見る
- 島（6x6 W32 fc32 = 846,225 μm²）は元から CONF_FF 込みなので測り直し不要
- 9/1 の構成メモリ抜きの値: SoPA 379,783 / IPGen 676,763 μm²。CONF_FF 1個 ≈ 20.6 μm²（6月の島レポート）なので
  込みの見込みは SoPA ≈ 593k / IPGen ≈ 887k / 島 846k（推測）
