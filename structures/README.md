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

## medium ベンチマーク（state_Medium_no_dec, 42回路, 2026-09-23）
small（41回路）で交互が効いたのが小規模特有かを確かめるための一式。alf と mogi は元 Verilog の文法エラー（入力名の抜け）で除外。
RTL → eblif は `RTL_DIR=rtl_medium OUTDIR=results/eblif_medium python3 src/rtl_to_eblif.py <回路名...>`、
中継挿入は `EBDIR=results/eblif_medium OUTDIR=results/eblif_relay_medium D0=99 python3 src/insert_relay.py`。
中継入り eblif は data/eblif_relay_medium/ に同梱（4.0MB）。

| ファイル | 規則 | 列数(入力側->FF側) | PA | 構成メモリ |
|---|---|---|---|---|
| superset_medium_s125_now.v | 今の規則 | [3,8,14,20,49,80,127,227,322,388,385,353,370,318,208,122,69,40,20,12] | 3,135 | 50,130 bit |
| superset_medium_s125_cyclic_eq.v | 巡回 | 同上 | 3,135 | 50,130 bit |
| superset_medium_s125_alt_cyc.v | 交互 | 同上 | 3,135 | 50,130 bit |

列数1.25倍（占有率80%）。3種とも列数・MUX・bit は完全に同一で、違うのは配線の相手だけ。
配線とツールの候補表が 6,264 入力すべて一致することを確認済み。
配置配線: `STEP=4 TOOL=place_fixed_tbl.py CAND_RULE=<規則> SUPERSET=structures/superset_medium_s125_<規則>.v EBR=... ./run_noskip_superset.sh`

## 幅の減少部だけ複製した専用構造（2026-09-24、dup_dec/）
「詰まりは FF 側の列数が減る帯にあり、複製は入力側にしか効かない」ことが分かったので、
列数が減り始める行から FF 側だけ fanout≤1 に複製した専用構造（余白ゼロ・全中継）。
中継入り eblif は data/eblif_dup_dec/ に同梱。作り方:
  `MAXF=1 MINROW=<減り始める行> python3 src/dup_fanout.py <in> <out>`（MINROW は 9/24 に追加）
  `EBDIR=data/eblif_dup_dec OUTDIR=structures/dup_dec SKIP_SPECS=2:0 python3 src/gen_ext_uniform_all.py <回路>`
| 回路 | MINROW | セル 前→後 | config 前→後 | 複製なし・今の規則 |
|---|---|---|---|---|
| indep | 6 | 170→178 (+4.7%) | 2,026→2,122 | INFEASIBLE 1s |
| lift | 5 | 257→304 (+18.3%) | 3,080→3,662 | INFEASIBLE |
| e7 | 8 | 531→570 (+7.3%) | 6,315→6,836 | INFEASIBLE 31s |
| e2 | 7 | 598→633 (+5.9%) | 8,374→8,856 | INFEASIBLE |
| lcu | 7 | 517→610 (+18.0%) | 6,893→8,146 | INFEASIBLE |
| e16 | 7 | 642→719 (+12.0%) | 7,679→8,644 | INFEASIBLE 44s |
手元での既知の結果: indep は今の規則 600s 決着せず / 巡回 OPTIMAL 14〜21s / 交互 600s 決着せず。

## ★スーパーセット：幅の減少部だけ複製したネットリスト版（2026-09-25、superset_dupdec_*.v）
41回路それぞれで「列数が前の行より減り始める行」から FF 側だけ fanout<=1 に複製（dup_fanout.py MAXF=1 MINROW=<回路ごと>）。
中継入り・減少部複製済みの eblif 41本を data/eblif_relay_dupdec/ に同梱（1.7MB）。セル合計 13,407 → 14,443（+7.7%）。
超集合の列数（入力側->FF側、列数1.0倍）:
  前（複製なし, superset_allrelay.v） [1,3,4,9,14,21,30,43,72,97,119,131,99,64,43,23,12,7] = 792PA / 11,083bit
  後（減少部だけ複製）               [1,3,4,9,14,21,30,43,72,97,119,134,119,78,44,24,12,7] = 831PA / 11,629bit（+4.9%）
  変わったのは行11〜15 だけ（+3,+20,+14,+1,+1）。3規則とも列数・MUX・bit 同一、配線 1,660 入力で検証済み。
配置: `STEP=4 TOOL=place_fixed_tbl.py CAND_RULE=<規則> SUPERSET=structures/superset_dupdec_<規則>.v EBR=data/eblif_relay_dupdec PLACED=results/place_dupdec_<規則> ./run_noskip_superset.sh`
  列数1.25倍版（superset_dupdec_s125_*.v, 9/25）: [2,4,5,12,18,27,38,54,90,122,149,168,149,98,55,30,15,9] = 1,045PA / 16,003bit
    （複製なしの s125 は 996PA / 15,189bit → +4.9% / +5.4%）

## 位置で規則を切り替えた版（2026-09-25、superset_allrelay_s125_split11.v）
列数1.25倍・複製なし（996PA / 15,189bit、s125 の他版と同一）。候補表は CAND_RULE=split11:
行き先の行番号 <=11（行10→行11 まで）は今の規則、行11→行12 以降（FF 側）は巡回（cyclic_eq）。
狙い: 入力側は多くに配るセルの受け皿（万能列）を残し、FF 側は届く先の少ない列を無くす。
配置: `STEP=4 TOOL=place_fixed_tbl.py CAND_RULE=split11 SUPERSET=structures/superset_allrelay_s125_split11.v ./run_noskip_superset.sh`

## 列数の増減で規則を切り替えた版（2026-09-25、CAND_RULE=grow_now）
行間ごとに、次の行の列数が増えるなら今の規則、減るなら巡回（cyclic_eq）。行番号で区切れない medium 用。
- superset_medium_s125_grow_now.v（3,135PA / 50,130bit）: 行間の規則 = 今×9, 巡×2, 今×1（行11→12: 353→370）, 巡×7
- small は完全な山形なので split11 と同一になる（structures/superset_allrelay_s125_split11.v を使う）
配置: `STEP=4 TOOL=place_fixed_tbl.py CAND_RULE=grow_now SUPERSET=structures/superset_medium_s125_grow_now.v EBR=data/eblif_relay_medium PLACED=results/place_medium_grow ./run_noskip_superset.sh`
