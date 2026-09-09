# structures/ — 41回路スーパーセットの配線構造 Verilog（2026-09-09）

18段・FF側揃え・|PI|=45 一律・同じ 41 回路（data/eblif_from_rtl）から生成。`run_noskip_superset.sh` の①〜③で再生成できる。
面積は 45nm gscl45nm、DC compile_ultra、**構成メモリ（CONF_FF チェーン）込み**（area/ 参照）。

| ファイル | 段飛びの運び方 | 総PA | skip本 | 構成メモリ | 面積 [μm²] | 載った回路 | 再生成 |
|---|---|---|---|---|---|---|---|
| superset_skip.v | 全部 skip（8/31 の superset.v と同一） | 486 | 452 | 10,350 bit | 586,318 | 41/41 | `D0=2` |
| superset_gap2relay.v | gap2 は中継、gap≥3 は skip（ケース(1)） | 576 | 287 | 10,580 | 575,672 | 39/41（bridge, e4 未決着） | `D0=3` |
| superset_gap3relay.v | gap2,3 は中継、gap≥4 は skip（ケース(2)） | 664 | 182 | 11,353 | 590,325 | 32/41 | `D0=4` |
| superset_allrelay.v | 全部中継（skip なし） | 792 | 0 | 11,083 | 543,682 | 26/41 | `D0=99` |
| superset_allrelay_margin8-13x3.v | 全部中継 ＋ 段8〜13 に +3 枠 | 810 | 0 | 11,335 | （未測定） | 残り15回路 0/15（7,200s） | `D0=99 MARGIN_SPEC=8-13:3` |

配置は段固定 CP-SAT（src/place_fixed_tbl.py、表制約版）、iidalab JOBS=8 ATIME=3,600〜7,200s。「載った」は OPTIMAL、未決着は UNKNOWN（INFEASIBLE は全構造で 0）。
中継 = 素通しに設定した PA（I_B=1, MODE=00）。中継入り eblif は `insert_relay.py`（D0）で作る。

トップモジュールは `cone`（CLK, PAE_RST_N, I[1:0], EXT[44:0], pa_o[6:0], CONFIG_DATA[N-1:0]）。
構成メモリ込みの面積測定用トップ（SOPA_CORE）は `src/gen_conf_chain.py <構造.v> <出力.v>` で付ける。
