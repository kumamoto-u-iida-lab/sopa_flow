# sopa_flow

SoPA（提案する eFPGA 配線構造）に、FSMベンチマークを **RTL から配置配線まで通す**ための最小構成。

```
元RTL (.v) →①→ ネットリスト(eblif) →②→ 配線構造(.v) →③→ 配置配線 →④→ bitstream →⑤→ 検証
```

## 必要なもの

| | 用途 | 入れ方 |
|---|---|---|
| Python 3 | 全部 | |
| **ortools** | ③の配置配線 (CP-SAT) | `pip install ortools` |
| **yosys** | ①の論理合成 | PATH に置くか `YOSYS=<パス>` |
| **Gurobi + ライセンス** | ①のテクノロジマッピング(ILP) | `~/gurobi.lic` か `GRB_LICENSE_FILE` |
| iverilog | ⑤' のシミュレーション（任意） | oss-cad-suite など。`SIMBIN=<bin>` |

**②③に Gurobi は不要**です。eblif さえあれば ortools だけで動きます。

Ubuntu 24.04 など PEP 668 の環境では `pip install` が弾かれるので venv を使ってください。

```bash
python3 -m venv ~/venv_sopa
source ~/venv_sopa/bin/activate     # tcsh なら activate.csh
pip install ortools
```

## 環境の点検

```bash
python3 src/sopa_paths.py
```

必要物が揃っているかを1つずつ表示します。足りなければ、どの環境変数で指定するかも出ます。

## 使い方

```bash
cd src

# ① RTL → eblif（Gurobi が要る）
python3 rtl_to_eblif.py girl10
#   → results/eblif_from_rtl/girl10/mapped_girl10.v.eblif

# ② eblif → その回路専用の最小構造
EBDIR=../results/eblif_from_rtl python3 gen_ext_uniform_all.py girl10
#   → results/cone_ext_uniform/girl10.v （+ index.csv）

# ③ 配置配線
ATIME=600 FFLAST=1 python3 place_ft_cone.py \
    ../results/eblif_from_rtl/girl10/mapped_girl10.v.eblif \
    ../results/cone_ext_uniform/girl10.v
```

①②はまとめても打てます。

```bash
FROM_RTL=1 python3 gen_ext_uniform_all.py girl10
```

```bash
# ④ bitstream と、構成メモリを焼き込んだ Verilog(Impl)
python3 gen_config_verilog.py \
    ../results/eblif_from_rtl/girl10/mapped_girl10.v.eblif \
    ../results/cone_ext_uniform/girl10.v \
    place_ft_cone_girl10.json \
    ../results/impl_girl10.v
#   → results/impl_girl10.v  構成を焼き込んだVerilog
#     results/girl10.bit      bitstream（0/1のASCII 1行・長さ=config幅）
#     results/girl10_io.txt   I/O対応表

# ⑤ 等価検証（yosys の SAT。元RTL と Impl が同じ動きをするか）
./equiv_check.sh girl10 16
#   → girl10: EQUIVALENT  (16段, 全入力組合せ網羅)

# ⑤' シミュレーション（iverilog が要る。tbで元RTLと毎サイクル照合）
python3 gen_tb_sopa.py ../results/impl_girl10.v      # tbを作る
SIMBIN=<oss-cad-suite/bin> python3 run_all_sim.py girl10
```

### girl10 で期待される出力

```
5) make_eblif -> .../mapped_girl10.v.eblif  (cell=44, DFF=3)
girl10  cells=38 D=7 |PI|=9 skip需要=4 config=467 OK
girl10: セル38 / must4 / D=7 widths=[1, 4, 6, 10, 8, 6, 4] / skipトラック4本 / 総スロット39
  FFfb対象 1信号 / FF段 [6] (入辺ありのため対象外 3信号)
結果: OPTIMAL (0s)
```

## 主な環境変数

```
共通    SOPA_ROOT   リポジトリのルート（既定: このディレクトリ）
①      YOSYS       yosys のパス      RTL_DIR  元RTLの場所（既定 rtl/）
        OUTDIR      eblif の出力先     KEEP=1   中間ファイルを残す
②      EBDIR       eblif を探す場所   MARGIN=1 縮小段に+1本（載らないときの救済）
        FROM_RTL=1  ①を先に流す
③      ATIME       上限秒数（既定300） FFLAST=1 must を最下段ちょうどに固定
        WORKERS     CP-SATのスレッド数  MINREL=0 中継の最小化を切る
```

## 構成

```
src/        ツール8本
  rtl_to_eblif.py         ① RTL → eblif（yosys + techmap + Gurobi ILP）
  gen_ext_uniform_all.py  ② eblif → 構造（回路ごとの最小構成）
  gen_cone_ext.py         ②の本体。構造Verilogを書く
  place_ft_cone.py        ③ 配置配線（CP-SAT）。中継とskip相乗りに対応
  place_skip_cone.py      ③の旧版（既存結果の再現用）
  place_greedy.py         eblif を読む load()
  sopa_paths.py           場所の解決と環境点検
  superset_profile.py     全回路の包絡線を数える（スーパーセット構造の設計用）
  gen_config_verilog.py   ④ 配置結果 → bitstream と構成済みVerilog
  equiv_check.sh          ⑤ yosysのSATで元RTLとの等価性を証明（iverilog不要）
  gen_tb_sopa.py          ⑤' Ref(元RTL)とImpl(SoPA)を並べて毎サイクル照合するtbを作る
  run_all_sim.py          ⑤' iverilog で実際にシミュレーションする
techmap/    テクノロジマッピング（main.py / ilp_gurobi.py / make_eblif.py / PA.xml）
pylib/      blif の前処理（BitstreamGen.PreProcess.*）
lib/        mycells.lib（DFF_PN0 の定義元。全FFが同型になる理由）
rtl/        元RTL 43回路
results/    生成物（gitには入れない）
```

## 用語

- **PA** … 2入力1出力・MODE 2bit の基本セル。`O = (A & (B ^ p0)) ^ p1`
- **段(stage)** … FFからの最長距離で決まる層。段 D−1 が最下段（FF側）
- **must** … 最下段に固定されるセル ＝ FFのD入力を駆動するセル ＋ 組合せPO 1個
- **組合せPO** … 外部出力のうち DFF の Q でないもの。全43回路でちょうど1個
- **FFfb** … 最下段の全PA出力が FLIPFLOP_NODE を通って全段の全IMUXの候補に入る配線
- **skip** … 段を飛び越える配線。(行き先段, 距離) ごとに本数を持つ
- **中継(フィードスルー)** … PAを素通しに設定して信号を運ぶこと。追加configは 0bit

## 注意

- `results/` の中身は生成物です。`.gitignore` で除外しています
- ③の結果 `UNKNOWN` は「載らない」ではなく**時間切れ**です。`ATIME` を伸ばしてください
  （`OPTIMAL`＝載る、`INFEASIBLE`＝載らないことの証明、が確定解）
- ③はメモリを食います。並列で回すなら **同時本数 ≒ 空きメモリ(GB) ÷ 2** が目安です
- ⑤の SAT は**有限段（既定16段）の証明**です。またクロック極性の誤りは検出できません
  （`sat -seq` はFFを1段進めるモデルでクロック信号を見ないため）。そこは ⑤' の
  シミュレーションが捕まえます。2026-08-06 に実測で確認済み

## ⚠️ 未検証（2026-08-31 時点）

**中継(フィードスルー)が1個以上入った配置での ④bitstream 生成は確かめていません。**

③ `place_ft_cone.py` は、空いているスロットを「素通しのPA」に転用して信号を運ぶこと
（＝中継）ができます。ネットリストには無いセルが配置に現れるので、④がそれを正しく
構成メモリに落とせるかは別問題です。

```
確認済み   girl10 / cat  … どちらも中継0個で ①→⑤ 通過（⑤ EQUIVALENT）
未確認     中継が要る回路（例: sortmax は中継1個で載る。2026-08-23 に確認）
```

中継が入った回路で④が落ちたり、⑤が NOT EQUIVALENT になったら、この件を疑ってください。
③の出力 json の `relay` が空でなければ中継が入っています。

```bash
python3 -c "import json;print(json.load(open('place_ft_cone_<回路>.json'))['relay'])"
```

## skip無しスーパーセット実験（2026-09-02 追加）

**問い**: skip配線を一切持たない構造（PA＋隣接配線＋外部入力だけ）に41回路すべてが載るか。
段飛び辺はすべて**中継**（素通しに設定したPA。`I_B=1, MODE=00` で `O=A`、追加の構成メモリ0bit）で運ぶ。

段固定（段 = D−1−R、R = FFまでの最長距離）では、段飛び辺「s(段c)→u(段c+g)」に要る中継の
段と個数は SAT を回さなくても決まる（段 c+1..c+g−1 に1個ずつ。同じ信号の読み手が複数なら
鎖は1本で、最遠の読み手までの g−1 個）。だから**ネットリストにセルを足すだけ**で、
行だけ解く段固定ツール `place_fixed_skip_ext.py` がそのまま使える。

```bash
JOBS=4 ATIME=3600 ./run_noskip_superset.sh          # ①〜④ 全部（④だけがSAT）
STEP=4 JOBS=4 ATIME=7200 ./run_noskip_superset.sh e4 e2   # ④だけ・回路を絞って再実行
```
| 手順 | ツール | 出力 |
|---|---|---|
| ① 中継挿入 | `src/insert_relay.py` | `results/eblif_relay/<回路>/mapped_<回路>.v.eblif` |
| ② 回路ごとの skip無し構造（幅を数えるだけ） | `gen_ext_uniform_all.py`（`SKIP_SPECS=2:0`） | `results/cone_noskip/` |
| ③ 包絡線 → スーパーセット | `superset_profile.py` → `src/gen_superset.py` | `results/superset_noskip.v` |
| ④ 41回路を段固定で配置 | `src/place_fixed_skip_ext.py` | `results/noskip_place/<回路>.log`, `summary.csv` |

`data/eblif_from_rtl/` に41回路の eblif（元RTL由来、2026-08-06 版）を同梱した。
①は Gurobi が要るので、ライセンスの無いマシンでもここから始められるようにするため。

ローカル(2026-09-02)で①〜③まで確認済み: D=18 / 総PA 792 / 最大幅 131 / CONFIG 11,083bit
（skip有りスーパーセットは総PA 486 / CONFIG 10,350bit）。④は未実施（iidalab で回す）。

⚠️ ④はメモリを食う。7.6GB のマシンでは CP-SAT が OOM killer に殺された（1本あたり最大 1.7GB 超）。
`JOBS` は 空きメモリ(GB)÷2 を目安に。

### 配置ツールの選択（2026-09-02 追記）
`src/place_fixed_tbl.py` は `place_fixed_skip_ext.py` と**同じ問題**を、辺1本＝表制約
（`AddAllowedAssignments`）1個で符号化した版。変数の数が 1/幅 程度に減る。
```
ass13 を skip無し超集合へ:  旧符号化 3,068秒(iidalab) → 表制約 112秒(ローカル)
bridge（占有率1.00の段あり）: どちらも 3,600秒/900秒で UNKNOWN
```
UNKNOWN が出た回路の再実行は `STEP=4 TOOL=place_fixed_tbl.py JOBS=8 ATIME=7200 ./run_noskip_superset.sh dmac bridge ...`。
`src/place_sa_fixed.py`（IPGen の SA を移植した版）は girl10 以外で収束しなかった（記録用に残す）。
