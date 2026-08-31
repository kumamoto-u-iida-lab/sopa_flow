#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sopa_paths.py — SoPAツール群が使う場所を1か所で決める。

このリポジトリだけで完結するのが既定。別環境へ持って行っても、
リポジトリを丸ごと置いて `yosys` と `gurobipy` があれば動く。
どうしても場所を変えたいときだけ環境変数で上書きする。

  SOPA_ROOT   リポジトリのルート     (既定: このファイルの1つ上)
  RTL_DIR     元RTL(.v)の場所        (既定: rtl/)
  YOSYS       yosys実行ファイル      (既定: PATH上の yosys)
  YOSYS_LIB   FF定義のliberty        (既定: lib/mycells.lib)
  TECHMAP_DIR テクノロジマッピング   (既定: techmap/)
  BSGEN_SRC   BitstreamGenのsrc      (既定: pylib/  ※BitstreamGen.PreProcess.* を import する)
  WORK_DIR    生成物の置き場         (既定: results/)

★2026-08-31: sopa_flow 用に構成を簡素化した(src/techmap/lib/rtl/pylib)。
  旧構成(benchmarks/ tools/*/...)も候補に残してあるので、どちらでも動く。
"""
import os, glob, shutil

SOPA_ROOT = os.environ.get("SOPA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _first(cands, what, envkey):
    """候補の中で実在する最初のパスを返す。無ければ分かりやすく落とす。"""
    v = os.environ.get(envkey)
    if v:
        if os.path.exists(v):
            return v
        raise FileNotFoundError(f"{envkey}={v} が存在しない ({what})")
    for c in cands:
        for p in sorted(glob.glob(c)):
            if os.path.exists(p):
                return p
    raise FileNotFoundError(
        f"{what} が見つからない。環境変数 {envkey} で指定してください。\n  探した場所:\n    "
        + "\n    ".join(cands))


def rtl_dir():
    return _first([os.path.join(SOPA_ROOT, "rtl"),
                   os.path.join(SOPA_ROOT, "benchmarks", "state_Small_no_dec", "Verilog")],
                  "元RTLのディレクトリ", "RTL_DIR")


def yosys():
    v = os.environ.get("YOSYS")
    if v:
        if os.path.exists(v) or shutil.which(v):
            return v
        raise FileNotFoundError(f"YOSYS={v} が実行できない")
    w = shutil.which("yosys")
    if w:
        return w
    raise FileNotFoundError("yosys が PATH にない。環境変数 YOSYS でパスを指定してください。")


def yosys_lib():
    return _first([os.path.join(SOPA_ROOT, "lib", "mycells.lib"),
                   os.path.join(SOPA_ROOT, "tools", "*", "libs", "YosysCells", "mycells.lib")],
                  "mycells.lib (FF定義のliberty)", "YOSYS_LIB")


def techmap_dir():
    return _first([os.path.join(SOPA_ROOT, "techmap"),
                   os.path.join(SOPA_ROOT, "tools", "techmap")],
                  "techmap ディレクトリ", "TECHMAP_DIR")


def pa_xml():
    return os.path.join(techmap_dir(), "patterngraph", "PA.xml")


def bsgen_src():
    # BitstreamGen.PreProcess.* を import できるディレクトリを返す
    return _first([os.path.join(SOPA_ROOT, "pylib"),
                   os.path.join(SOPA_ROOT, "tools", "*", "src")],
                  "BitstreamGen の src (blif前処理)", "BSGEN_SRC")


def work_dir():
    d = os.environ.get("WORK_DIR") or os.path.join(SOPA_ROOT, "results")
    os.makedirs(d, exist_ok=True)
    return d


def check_all(verbose=True):
    """必要物が揃っているか点検する。揃っていなければ足りないものを列挙して返す。"""
    items = [("SOPA_ROOT", lambda: SOPA_ROOT), ("元RTL", rtl_dir), ("yosys", yosys),
             ("mycells.lib", yosys_lib), ("techmap", techmap_dir), ("PA.xml", pa_xml),
             ("BitstreamGen src", bsgen_src)]
    missing = []
    for name, fn in items:
        try:
            p = fn()
            if not os.path.exists(p) and not shutil.which(p):
                raise FileNotFoundError(p)
            if verbose:
                print(f"  OK   {name:18s} {p}")
        except Exception as e:
            missing.append(name)
            if verbose:
                print(f"  無し {name:18s} {e}")
    try:
        import gurobipy
        if verbose:
            print(f"  OK   {'gurobipy':18s} {gurobipy.gurobi.version()}")
    except Exception as e:
        missing.append("gurobipy")
        if verbose:
            print(f"  無し {'gurobipy':18s} {e}")
    return missing


if __name__ == "__main__":
    print(f"SOPA_ROOT = {SOPA_ROOT}\n環境の点検:")
    m = check_all()
    print("\n" + ("すべて揃っています。" if not m else f"足りないもの: {', '.join(m)}"))
    raise SystemExit(1 if m else 0)
