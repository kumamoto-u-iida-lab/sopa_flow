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

## FF を下3行に置いた medium 1.25倍版（2026-09-28、superset_medium_s125_ff3_{now,cyclic_eq,alt_cyc,grow_now}.v）
gen_cone_ext.py の NFFSTAGES=3（行17・18・19 の全 PA 出力に FLIPFLOP_NODE、72個）。列数は medium 1.25倍と同じ。
構成メモリ 56,454bit（FF 最下行だけの版 50,130bit から +12.6%。FF帰還が全 IMUX に入るので imux が +6,264bit）。
place_fixed_off.py（段固定＋OFFSET）で OFFSET=0/1/2 のどれでも物理的に正当（FF段 = 19/18/17）。
配置: `STEP=4 TOOL=place_fixed_off.py OFFSET=<0|1|2> CAND_RULE=<規則> SUPERSET=structures/superset_medium_s125_ff3_<規則>.v PLACED=... ./run_noskip_superset.sh`

## FF を下3行に置いた small 1.25倍版（2026-09-28、superset_allrelay_s125_ff3_{now,cyclic_eq,alt_cyc,split11}.v）
NFFSTAGES=3（行15・16・17 の全 PA 出力に FF、53個）。列数は small 1.25倍（996PA）と同じ。15,961bit（FF最下行だけの 15,189bit から +5.1%）。
回路ごとに OFFSET=0,1,2 を順に試すには run_off_sweep.sh を使う（place_fixed_off.py は FF の無い段へのずらしを弾く）。

## 余りの割合をそろえた20段構造（2026-10-04、superset_mm20ff7_alt_cyc.v）
総PA 1,050・20段・最終段7（FF 6個＋組合せ出力1）・交互（alt_cyc）。small 41回路が **41/41**（e4 1,560s が最遅）。
幅の決め方は目的1つ:「合計1,050を固定し、各段の 幅÷必要数 の最小値を最大にする」。整数の水位合わせで一意に決まる
（必要数から始め、比が最小の段に1個ずつ足す。必要0の段は1、最終段は7に固定）。
必要数 = small 41回路を FF 側に揃えたときの各段の最大（20段に揃えたもの）。※ネットリスト由来。
| ファイル | 列数(入力側->FF側) | PA | 構成メモリ |
|---|---|---|---|
| superset_mm20ff7_alt_cyc.v | [1,1,2,4,6,12,19,28,40,57,95,128,157,173,131,85,57,31,16,7] | 1,050 | 14,695 bit（IMUX 12,588 + PA 2,100 + FF 7） |
再生成:
```bash
cd src && CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0$(printf ',45%.0s' $(seq 19)) NEXTTAG=mm20ff7_alt_cyc \
  python3 gen_cone_ext.py 7,16,31,57,85,131,173,157,128,95,57,40,28,19,12,6,4,2,1,1
```
比較: 倍々の規則で作った同じ 1,050PA・14,695bit の構造（1,2,3,4,7,10,17,27,43,68,110,135,135,135,136,112,56,28,14,7）は 38/41。
面積用（構成メモリ込み、top=SOPA_CORE）: `python3 src/gen_conf_chain.py structures/superset_mm20ff7_alt_cyc.v area/rtl/sopa_conf/superset_mm20ff7_alt_cyc.v`
配置: `STEP=4 TOOL=place_fixed_tbl.py CAND_RULE=alt_cyc SUPERSET=structures/superset_mm20ff7_alt_cyc.v ./run_noskip_superset.sh`

## 2026-10-06: 隣の段と2倍以内の規則を守った版
今の規則（gen_pattern）は前段の行 k の届く先を ⌊2×次段幅÷k⌋ 本にするので、前段が次段の2倍を超えると
後ろの行が次段のどこにもつながらない。superset_mm20ff7_alt_cyc.v は 16→7（2.29倍）で段18の行14・15が死んだPA → 使わない。
| ファイル | 列数(入力側->FF側) | PA | 構成メモリ | small 41（交互） |
|---|---|---|---|---|
| superset_mm20r2_alt_cyc.v | [1,1,2,4,6,12,19,28,40,58,96,129,158,174,132,85,56,28,14,7] | 1,050 | 14,695 bit | 段固定 41/41 |
| superset_r1536_alt_cyc.v | [1,2,2,4,6,10,15,24,38,61,95,151,238,448,224,112,56,28,14,7] | 1,536 | 22,741 bit | 段固定 38/41 ＋ 案B・子ごと 3/3 |
| superset_r1536_alt_cyc_ext45n.v | 同上 | 1,536 | 21,065 bit | 外部入力を FF 側ほど減らした入れ子版（下記）。結果待ち |
| superset_r1536pi_alt_cyc.v | [45,55×6,56,66,86,121,157,174,178,128,85,56,30,15,9] | 1,536 | 17,975 bit | 外部入力を IMUX に配らず PI ノード＋中継で運ぶ版（下記）。結果待ち |
mm20r2 = 合計1,050で「幅÷必要数の最小を最大化」＋隣2倍以内（必要数は small のネットリスト由来）。
r1536 = ネットリスト不使用の規則: FF 側は最終段7から倍々（段数は式 floor(1.21·log2(最大遷移数225)−2.90)=6）、入力側は段0=1から等比、20段。
再生成: `cd src && CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0$(printf ',45%.0s' $(seq 19)) NEXTTAG=<tag> python3 gen_cone_ext.py <FF側→入力側の幅>`
ext45n（2026-10-14）= r1536 と同じ幅・規則で、外部入力を FF 側の行0〜4=12本 / 5〜9=24本 / 10〜14=36本 / 15〜19=45本（入力側から NEXT=0,45×4,36×5,24×5,12×5）。
  各段には EXT の先頭 n 本だけが配られるので、PI→EXT 線の割り当ては入れ子の条件（src/ext_nest.py）を満たす必要がある。配置は run_ext_nest.sh（段固定→載らなければ案B・子ごと）。
r1536pi（2026-10-14）= 外部入力 EXT 45本は段0（45列）にだけ入る。段0 の PA i は EXT[i] を直結（I_B=1'b1, MODE 00 → 出力=EXT[i]）
  した PI ノードで、IMUX も選択ビットも無い（gen_cone_ext.py TOPEXT=1）。どの PI をどの EXT 線に流すかは回路ごとに自由。
  段1以降の IMUX には EXT を配らない。PI は PI ノードから中継の鎖で使う行まで下ろす（src/insert_pi_nodes.py、data/eblif_pinode）。
  列数 = small 41回路の PI ノード込みの行ごとの最大（包絡線）を、段0=45 に固定して残り 1,491 を 1.271倍で配る。合計 1,536、隣2倍以内、交互。
  再生成: `cd src && TOPEXT=1 CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0$(printf ',0%.0s' $(seq 19)) NEXTTAG=pinode python3 gen_cone_ext.py 9,15,30,56,85,128,178,174,157,121,86,66,56,55,55,55,55,55,55,45`

## PA 768 の構造（2026-10-20、superset_pi768_alt_cyc.v）
PA 768（1,536 の半分）で、載ると見込める回路だけを対象にしたスーパーセット。作り方は `src/select_pa_budget.py`:
① PI ノード入り（data/eblif_pinode）の配置する PA ≤ 768 の 34回路 → ② 包絡線 ≤ 768/1.2 になるまで PA の大きい順に外し（25回路）、micks を戻して 26回路・包絡線 649（余白 1.18倍）
→ ③ ff7 と同じ肉付け（行0=7、最上段=PI 最大の 20、隣2倍以内、倍率 f=1.182）。
列数（FF 側→入力側）[7,14,28,52,80,91,86,69,56,43,30,24×8,20]、768PA、8,327bit、外部入力バス 20本、IMUX 最大 18。
対象26回路と列数は results/pa768_select.json。再生成: `BUDGET=768 MARGIN=1.2 KEEP=micks python3 src/select_pa_budget.py` → 表示された列数で gen_cone_ext.py（ff7 と同じ環境変数）。

## 外部入力を「論理の1つ上」で受ける構造（2026-10-20、superset_pilocal_s120_alt_cyc.v）
ユーザー案。行19 だけに外部入力を入れて鎖で運ぶ方式（PI ノード 7,713個）をやめ、PI ノードを回路ごとに論理の一番上の行の1つ上に置く。
- ネットリスト: `OUTDIR=data/eblif_pilocal TOP=local python3 src/insert_pi_nodes.py`（41回路、運ぶためのセル 3,584、合計 16,991）
- 構造: 行1〜17 の PA j の ia に専用の EXT[j mod 45] を1本だけ足す（ib・FF の行には足さない）、段0（最上段）は EXT[j mod 45] 直結。
  `EXTDED=45 TOPEXT=1 CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0×19 NEXTTAG=pilocal gen_cone_ext.py <列数>`
- 列数: `EBDIR=data/eblif_pilocal NROW=19 SCALE=1.2 python3 src/envelope_widths.py` → 包絡線 1,072 ×1.2 = [7,14,28,53,81,122,168,165,149,114,82,63,53,52,34,30,27,24,23]
  1,289PA、14,917bit、19段（行19 は無し）。
- 配置: place_fixed_tbl.py / place_span_tbl.py / check_span.py が見出しの EXTDED を読み、PI ごとに線を1本（全部違う線）、PI ノードは「列 mod 45 = 線」の列だけ。

## EXT を受ける列を行ごとに絞った r1536（2026-10-21、superset_r1536_xc_<選び方>_alt_cyc.v）
ミーティングの問い「外部入力をフィードスルーで運ぶのが本当にあるべき姿か」を受けて、PI ノードを使わない方式を、PA 数をそろえて（1,536）比べる。
- 土台 r1536（列数・候補表は同じ）。② 中継入りネットリスト（論理セルが PI を直接読む）。
- 行 h で EXT 45本を受ける列 = ② の 41回路で「PI を読む論理セル」の最大 m_h × 1.2（切り上げ）、計 195列。ia・ib 両方に 45本。
  m_h（FF 側から）= [0,2,4,7,7,11,17,23,24,23,15,6,5,5,5,0,2,1]
- 列の選び方 EXTSEL: head（先頭）/ tail（末尾）/ even（等間隔）/ reach2（次段の2列以上に届く列から等間隔）。
  `EXTM=0,0,2,3,0,6,6,6,8,18,28,29,28,21,14,9,9,5,3,0 EXTSEL=<選び方> CAND_RULE=alt_cyc SKIP_SPECS=2:0 NEXT=0,45×19 gen_cone_ext.py 7,14,28,56,112,224,448,238,151,95,61,38,24,15,10,6,4,2,2,1`
- 18,593〜18,619bit（r1536 22,741 / ff7 17,699）、IMUX 入力総数 74,868（r1536 195,468）。配置は `bash run_xc.sh`。
- 配置ツール（place_fixed_tbl / place_span_tbl / check_span）は見出し2行目の `// EXTCOLS` を読み、PI を読むセルを EXT の列に限る。
- 手元 girl10: head 段固定 INFEASIBLE・案B OPTIMAL / even 段固定 OPTIMAL・案B OPTIMAL、検算誤り0。

## pilocal を PA 数 1,152〜3,072 で（2026-10-22、superset_pilocal_pa<N>_alt_cyc.v）
FatTree の CLB 内 PAE 数 6/8/10/12/16（64 CLB → 384〜1,024 PAE、×3）と収容能力をそろえる。従来 PA。
ネットリスト data/eblif_pilocal は最大19段 → 構造は20段（足した行19 = 行18 と同じ列数、EXT 直結。案B で PI ノードを上げる置き場）。
`EBDIR=data/eblif_pilocal NROW=19 EXTRA=1 TOTAL=<N> python3 src/envelope_widths.py` → gen_cone_ext.py（EXTDED=45 TOPEXT=1 alt_cyc）
| PA | 倍率 | bit | IMUX 入力総数 | 列数（FF 側→入力側） |
|---|---|---|---|---|
| 1,152 | ≈1.07 | 13,220 | 40,453 | [7,13,26,47,71,106,147,144,130,100,72,55,47,45,30,27,24,21,20,20] |
| 1,536 | ≈1.43 | 17,856 | 55,730 | [7,14,28,56,96,144,199,195,176,135,97,74,63,61,40,36,32,29,27,27] |
| 1,920 | | 22,447 | 71,400 | [7,14,28,56,112,183,254,248,225,172,124,95,80,78,51,46,40,37,35,35] |
| 2,304 | | 27,051 | 87,402 | [7,14,28,56,112,224,311,305,276,211,151,116,98,96,63,56,49,45,43,43] |
| 3,072 | | 36,218 | 120,119 | [7,14,28,56,112,224,440,430,390,299,214,164,139,135,88,79,70,63,60,60] |
配置: `bash run_pilocal_sweep.sh`。★10/22 修正: EXTDED 構造の最上段に PI ノード以外を置かない（place_span_tbl / check_span）。
