# sopa_flow

SoPA（提案する eFPGA 配線構造）に、FSMベンチマークを **RTL から配置配線まで通す**ための最小構成。

```
元RTL (.v)  →①→  ネットリスト (eblif)  →②→  配線構造 (.v)  →③→  配置配線
```

## 必要なもの

| | 用途 | 入れ方 |
|---|---|---|
| Python 3 | 全部 | |
| **ortools** | ③の配置配線 (CP-SAT) | `pip install ortools` |
| **yosys** | ①の論理合成 | PATH に置くか `YOSYS=<パス>` |
| **Gurobi + ライセンス** | ①のテクノロジマッピング(ILP) | `~/gurobi.lic` か `GRB_LICENSE_FILE` |

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
