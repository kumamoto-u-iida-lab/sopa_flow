# structures/ — 41回路スーパーセットの配線構造 Verilog（2026-09-09）

18段・FF側揃え・|PI|=45 一律・同じ 41 回路（data/eblif_from_rtl）から生成。`run_noskip_superset.sh` の①〜③で再生成できる。
面積は 45nm gscl45nm、DC compile_ultra、**構成メモリ（CONF_FF チェーン）込み**（area/ 参照）。

| ファイル | 段飛びの運び方 | 総PA | skip本 | 構成メモリ | 面積 [μm²] | 載った回路 | 再生成 |
|---|---|---|---|---|---|---|---|
| superset_skip.v | 全部 skip（8/31 の superset.v と同一） | 486 | 452 | 10,350 bit | 586,318 | 41/41 | `D0=2` |
| superset_gap2relay.v | gap2 は中継、gap≥3 は skip（ケース(1)） | 576 | 287 | 10,580 | 575,672 | 39/41（bridge, e4 未決着） | `D0=3` |
| superset_gap3relay.v | gap2,3 は中継、gap≥4 は skip（ケース(2)） | 664 | 182 | 11,353 | 590,325 | 32/41 | `D0=4` |
| superset_allrelay.v | 全部中継（skip なし） | 792 | 0 | 11,083 | 543,682 | 26/41 | `D0=99` |
| superset_allrelay_cyclic_eq.v | 全部中継・**候補表を巡回（本数そろえ版 cyclic_eq）**。幅・MUX の大きさ・bit は superset_allrelay.v と同一、つなぎ先だけ違う（9/17） | 792 | 0 | 11,083 | （測定中） | （未配置） | `CAND_RULE=cyclic_eq` gen_cone_ext.py（下記） |
| superset_allrelay_s125.v | 全部中継・**列数を 1.25 倍**（占有率 80%、切り上げ、FF も 7→9）。今の規則（9/19） | 996 | 0 | 15,189 | （未測定） | （未配置） | `SCALE=1.25 PROFILE=results/profile_d0_99.json` gen_superset.py |
| superset_allrelay_s125_cyclic_eq.v | 同上の配線を巡回（本数そろえ版）にした版（9/19） | 996 | 0 | 15,189 | （未測定） | （未配置） | 上に `CAND_RULE=cyclic_eq` を足す |
| superset_allrelay_s125_alt_cyc.v | 列数1.25倍・**行ごとに巡回と今の規則を交互**（alt_cyc: 行き先の行番号が偶数→巡回 / 奇数→今の規則）。列数・MUX・bit は s125 の他2版と同一（9/22） | 996 | 0 | 15,189 | （未測定） | （実行中） | `SCALE=1.25 CAND_RULE=alt_cyc` gen_superset.py |
| superset_allrelay_alt_cyc.v | 全部中継・**列数はそのまま**（792PA）で候補表を交互（alt_cyc）にした版。s125 の交互版が 41/41 だったので、列数 +25% が本当に要るかを確かめる用（9/22） | 792 | 0 | 11,083 | （未測定） | （実行中） | `CAND_RULE=alt_cyc PROFILE=results/profile_d0_99.json` gen_superset.py |
| superset_allrelay_margin8-13x3.v | 全部中継 ＋ 段8〜13 に +3 枠 | 810 | 0 | 11,335 | （未測定） | 残り15回路 0/15（7,200s） | `D0=99 MARGIN_SPEC=8-13:3` |

配置は段固定 CP-SAT（src/place_fixed_tbl.py、表制約版）、iidalab JOBS=8 ATIME=3,600〜7,200s。「載った」は OPTIMAL、未決着は UNKNOWN（INFEASIBLE は全構造で 0）。
中継 = 素通しに設定した PA（I_B=1, MODE=00）。中継入り eblif は `insert_relay.py`（D0）で作る。

トップモジュールは `cone`（CLK, PAE_RST_N, I[1:0], EXT[44:0], pa_o[6:0], CONFIG_DATA[N-1:0]）。
構成メモリ込みの面積測定用トップ（SOPA_CORE）は `src/gen_conf_chain.py <構造.v> <出力.v>` で付ける。

## 巡回版の再生成（2026-09-17）
```bash
cd src && CAND_RULE=cyclic_eq SKIP_SPECS=2:0 NEXT=0$(printf ',45%.0s' $(seq 17)) NEXTTAG=allrelay \
  python3 gen_cone_ext.py 7,12,23,43,64,99,131,119,97,72,43,30,21,14,9,4,3,1
```
CAND_RULE=now で同じコマンドを打つと superset_allrelay.v とコメント行以外 完全一致（確認済み）。
面積用: `python3 src/gen_conf_chain.py structures/superset_allrelay_cyclic_eq.v area/rtl/sopa_conf/superset_allrelay_cyclic_eq.v`（この1本だけ git 管理）
