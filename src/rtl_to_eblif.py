#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rtl_to_eblif.py — 元RTL(.v) から mapped_<回路>.v.eblif を生成する。

既存手法(BitstreamGeneratorMainSA_FF1.py)と同じ流れをそのまま再現する:
   read -sv / synth -flatten / dfflibmap -liberty mycells.lib / abc -g AND / write_blif
     -> BlifPreProcess(RemoveBuffer -> ModifyBuffer -> InsertBuffer)
     -> BlifConverter -> subjectgraph.xml
     -> techmap/src/main.py -> ilp_gurobi.py -> make_eblif.py -> mapped.eblif

出力: <OUTDIR>/<回路>/mapped_<回路>.v.eblif
  ※ result_state_small_patopae/ は上書きしない(既存の配置JSONが信号名に依存するため)。

 使い方:
   python3 rtl_to_eblif.py <回路名 or RTLパス> [...]        # 既定の RTL_DIR から探す
 環境変数:
   RTL_DIR   元RTLの場所 (既定 state_benchmark/state_Small_no_dec/Verilog)
   OUTDIR    出力先      (既定 full/eblif_from_rtl)
   YOSYS     yosysのパス (既定 prga/local/bin/yosys)
   KEEP=1    中間ファイル(blif/xml/json/log)を残す
"""
import sys, os, re, shutil, subprocess, tempfile

# ★2026-08-31: 場所の解決を sopa_paths.py に一本化した。
#   以前は yosys を絶対パスで直書きし、BSGen のディレクトリ名にも依存していたので
#   別マシン・別構成では動かなかった。sopa_paths は環境変数でも上書きできる。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sopa_paths as SP

SD = os.path.dirname(os.path.abspath(__file__))
ROOT = SP.SOPA_ROOT

YOSYS = SP.yosys()               # PATH上の yosys。無ければ環境変数 YOSYS で指定
LIB = SP.yosys_lib()             # lib/mycells.lib
TECHMAP = SP.techmap_dir()       # techmap/
PAXML = SP.pa_xml()              # techmap/patterngraph/PA.xml
BSG_SRC = SP.bsgen_src()         # pylib/ (BitstreamGen.PreProcess.* を import する)
RTL_DIR = SP.rtl_dir()           # rtl/
OUTDIR = os.environ.get("OUTDIR", os.path.join(SP.work_dir(), "eblif_from_rtl"))
KEEP = os.environ.get("KEEP") == "1"

YS = """read -sv {v}
synth -flatten -top {top}
dfflibmap -liberty {lib}
abc -g AND
write_blif {blif}
"""


def top_module(vfile):
    """既存手法(TopModuleExtractor)と同じ: 最初に現れる module 名をトップとする。"""
    m = re.search(r'\bmodule\s+(\w+)', open(vfile).read())
    if not m:
        raise ValueError(f"module が見つからない: {vfile}")
    return m.group(1)


def run(cmd, cwd, log, env=None):
    with open(os.path.join(cwd, log), "w") as f:
        r = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env)
    if r.returncode != 0:
        tail = open(os.path.join(cwd, log)).read().splitlines()[-6:]
        raise RuntimeError(f"{os.path.basename(cmd[0] if cmd[0] != sys.executable else cmd[1])} 失敗 "
                           f"(exit={r.returncode}):\n    " + "\n    ".join(tail))


def rtl_to_eblif(vfile, outdir=OUTDIR, workdir=None, verbose=True):
    """RTL .v -> mapped_<top>.v.eblif。生成した eblif のパスを返す。"""
    vfile = os.path.abspath(vfile)
    top = top_module(vfile)                                    # yosys の -top に渡すモジュール名
    name = os.path.splitext(os.path.basename(vfile))[0]        # 回路名は**ファイル名**で決める
    # ※ ass13_no_decoder.v の中身は module ass13。モジュール名で命名すると ass13 を上書きしてしまう。
    dst_dir = os.path.join(outdir, name)
    os.makedirs(dst_dir, exist_ok=True)
    tmp = workdir or tempfile.mkdtemp(prefix=f"rtl2eblif_{name}_")
    os.makedirs(tmp, exist_ok=True)
    say = (lambda s: print(s, flush=True)) if verbose else (lambda s: None)

    # 1) yosys 合成
    blif = os.path.join(tmp, f"{top}.blif")
    ysfile = os.path.join(tmp, "PreTechMapSynth.ys")
    open(ysfile, "w").write(YS.format(v=vfile, top=top, lib=LIB, blif=blif))
    run([YOSYS, ysfile], tmp, "yosys.log")
    say(f"  1) yosys      -> {os.path.basename(blif)}")

    # 2-3) blif 前処理 + XML 変換 (BSGen の PreProcess をそのまま使う)
    pre = f"""
import sys; sys.path.insert(0, {BSG_SRC!r})
from BitstreamGen.PreProcess.BlifPreProcess import BlifPreProcess
from BitstreamGen.PreProcess.BlifConverter import BlifConverter
pp = BlifPreProcess({blif!r})
pp.RemoveBuffer(); pp.ToFile('nobuf.blif')
pp.ModifyBuffer(); pp.ToFile('modbuf.blif')
pp.InsertBuffer(); pp.ToFile('addbuf.blif')
BlifConverter('addbuf.blif').ToXML('subjectgraph.xml')
"""
    open(os.path.join(tmp, "_pre.py"), "w").write(pre)
    run([sys.executable, "_pre.py"], tmp, "pre.log")
    say("  2) 前処理      -> addbuf.blif / subjectgraph.xml")

    # 4) テクノロジマッピング
    run([sys.executable, os.path.join(TECHMAP, "src", "main.py"), "./subjectgraph.xml", PAXML],
        tmp, "techmap.log")
    os.replace(os.path.join(tmp, "match_result_name.json"), os.path.join(tmp, f"match_result_{name}.json"))
    say("  3) techmap    -> match_result")

    # 5) ILP (Gurobi)
    run([sys.executable, os.path.join(TECHMAP, "src", "ilp_gurobi.py"),
         f"match_result_{name}.json", f"{name}.json"], tmp, "ilp.log")
    say("  4) ILP        -> 被覆決定")

    # 6) eblif 生成
    run([sys.executable, os.path.join(TECHMAP, "src", "make_eblif.py"),
         "./subjectgraph.xml", PAXML, f"{name}.json"], tmp, "make_eblif.log")

    dst = os.path.join(dst_dir, f"mapped_{name}.v.eblif")
    shutil.copyfile(os.path.join(tmp, "mapped.eblif"), dst)
    ncell = sum(1 for l in open(dst) if l.startswith(".subckt cell"))
    ndff = sum(1 for l in open(dst) if l.startswith(".subckt DFF"))
    say(f"  5) make_eblif -> {dst}  (cell={ncell}, DFF={ndff})")

    if KEEP:
        keep = os.path.join(dst_dir, "work")
        shutil.rmtree(keep, ignore_errors=True); shutil.copytree(tmp, keep)
        say(f"     中間ファイル: {keep}")
    if not workdir:
        shutil.rmtree(tmp, ignore_errors=True)
    return dst


def resolve_rtl(a):
    """回路名 or パス -> RTLの絶対パス"""
    if os.path.isfile(a):
        return a
    p = os.path.join(RTL_DIR, a if a.endswith(".v") else a + ".v")
    if not os.path.isfile(p):
        raise FileNotFoundError(f"RTLが見つからない: {a} (RTL_DIR={RTL_DIR})")
    return p


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    for chk, path in [("yosys", YOSYS), ("mycells.lib", LIB), ("PA.xml", PAXML)]:
        if not os.path.exists(path):
            sys.exit(f"必要ファイルが無い: {chk} -> {path}")
    ok = 0
    for a in args:
        v = resolve_rtl(a)
        print(f"[{os.path.basename(v)}] top={top_module(v)}", flush=True)
        try:
            rtl_to_eblif(v)
            ok += 1
        except Exception as e:
            print(f"  失敗: {e}", flush=True)
    print(f"\n=== {ok}/{len(args)} 生成  出力先: {OUTDIR} ===")
