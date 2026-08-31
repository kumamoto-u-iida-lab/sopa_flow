#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_all_sim.py — 各回路を実際にシミュレーションして、元RTLと出力が一致するか確かめる。

SAT等価検証(equiv_check.sh)が担保**しない**もの、とくに**クロックの極性**は
ここでしか確認できない。配置済み(place_..._<回路>.json がある)の回路が対象。

 使い方: python3 run_all_sim.py [回路名...]
 環境変数:
   SIMBIN=<dir>   iverilog / vvp のあるディレクトリ (既定: PATH)
   NPAT=200       印加パターン数
   STIME=600      1回路あたりの上限(秒)
   VCD=1          波形(.vcd)を残す (既定は消す。42回路分だと大きいため)
   SERIAL=1       案B(CONF_*でシリアル書き込み)で検証する。既定は案A(並列ポート)
 出力: results/verify/sim/summary.csv と 各回路のログ・tb一式
"""
import sys, os, re, csv, glob, time, shutil, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sopa_paths as SP

SD = os.path.dirname(os.path.abspath(__file__))
WORK = SP.work_dir()
EBDIR = os.path.join(WORK, "eblif_from_rtl")
CONE = os.path.join(SD, "cone_ext_uniform")
OUTD = os.path.join(WORK, "sim_serial" if os.environ.get("SERIAL")=="1" else "sim")
NPAT = os.environ.get("NPAT", "200")
STIME = int(os.environ.get("STIME", "600"))
KEEPVCD = os.environ.get("VCD") == "1"
SERIAL = os.environ.get("SERIAL") == "1"   # 案B: 既存eFPGAと同じシリアル書き込みで .bit をロードする
SIMBIN = os.environ.get("SIMBIN", "")
IVERILOG = os.path.join(SIMBIN, "iverilog") if SIMBIN else (shutil.which("iverilog") or "")
VVP = os.path.join(SIMBIN, "vvp") if SIMBIN else (shutil.which("vvp") or "")
os.makedirs(OUTD, exist_ok=True)

if not IVERILOG or not VVP:
    sys.exit("iverilog / vvp が見つかりません。SIMBIN=<binのあるdir> で指定してください。\n"
             "  例) OSS CAD Suite: SIMBIN=$HOME/oss-cad-suite/bin python3 run_all_sim.py")


def sh(cmd, log, cwd, timeout=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = (e.stdout or "") + (e.stderr or "") + f"\n[TIMEOUT {timeout}s]", 124
    with open(log, "a") as f:
        f.write(f"$ {' '.join(map(str, cmd))}\n{out}\n{'-'*60}\n")
    return rc, out


def one(ckt):
    """1回路: tb一式を作り、iverilogでコンパイルして実行し、PASS/FAIL を返す。"""
    d = os.path.join(OUTD, ckt)
    os.makedirs(d, exist_ok=True)
    log = os.path.join(d, "sim.log")
    open(log, "w").close()
    eb = os.path.join(EBDIR, ckt, f"mapped_{ckt}.v.eblif")
    cone = os.path.join(CONE, f"{ckt}.v")
    pj = os.path.join(SD, f"place_fixed_skip_ext_{ckt}.json")
    for f in (eb, cone, pj):
        if not os.path.exists(f):
            return "NO_PLACE", 0, 0

    # 1) Impl + .bit + I/O表。案A=CONFIG_DATAを並列ポート / 案B=CONF_*でシリアル書き込み
    env = dict(os.environ, **({"SERIAL": "1"} if SERIAL else {"CFGPORT": "1"}))
    r = subprocess.run([sys.executable, "gen_config_verilog.py", eb, cone, pj,
                        os.path.join(d, f"impl_{ckt}.v")],
                       cwd=SD, capture_output=True, text=True, env=env)
    open(log, "a").write(r.stdout + r.stderr + "\n" + "-"*60 + "\n")
    if not os.path.exists(os.path.join(d, f"impl_{ckt}.v")):
        return "IMPL_FAIL", 0, 0
    nbit = int((re.search(r'CONFIG=(\d+)bit', r.stdout) or re.search(r'(0)', "0")).group(1))

    # 2) tb 生成 + 参照RTL/構造を同じ場所へ
    rc, out = sh([sys.executable, "gen_tb_sopa.py", os.path.join(d, f"impl_{ckt}.v"), "-n", NPAT],
                 log, SD, timeout=120)
    if rc != 0:
        return "TB_FAIL", nbit, 0
    shutil.copyfile(cone, os.path.join(d, f"struct_{ckt}.v"))
    shutil.copyfile(os.path.join(SP.rtl_dir(), f"{ckt}.v"), os.path.join(d, f"ref_{ckt}.v"))

    # 3) コンパイル
    rc, out = sh([IVERILOG, "-g2012", "-o", "sim.vvp",
                  f"ref_{ckt}.v", f"struct_{ckt}.v", f"impl_{ckt}.v", f"tb_{ckt}.v"],
                 log, d, timeout=300)
    if rc != 0:
        return "COMPILE_FAIL", nbit, 0

    # 4) 実行
    rc, out = sh([VVP, "sim.vvp"], log, d, timeout=STIME)
    if not KEEPVCD:
        for f in glob.glob(os.path.join(d, "*.vcd")) + glob.glob(os.path.join(d, "*.vvp")):
            os.remove(f)
    m = re.search(r'\[(PASS|FAIL)\][^\n]*?(\d+)\s*(?:/\s*(\d+))?\s*checks', out)
    if not m:
        return ("TIMEOUT" if rc == 124 else "RUN_FAIL"), nbit, 0
    if m.group(1) == "PASS":
        return "PASS", nbit, int(m.group(2))
    return "FAIL", nbit, int(m.group(3) or 0)


circuits = sys.argv[1:] or sorted(
    os.path.basename(p).replace("place_fixed_skip_ext_", "").replace(".json", "")
    for p in glob.glob(os.path.join(SD, "place_fixed_skip_ext_*.json")))
print(f"対象 {len(circuits)}回路  パターン数={NPAT}  方式={'案B(シリアル書き込み)' if SERIAL else '案A(並列ポート)'}\n", flush=True)

rows = []
t0 = time.time()
for k, ckt in enumerate(circuits, 1):
    t1 = time.time()
    st, nbit, nchk = one(ckt)
    dt = round(time.time() - t1)
    rows.append((ckt, nbit, st, nchk, dt))
    mark = {"PASS": "一致", "FAIL": "不一致"}.get(st, st)
    print(f"[{k:2d}/{len(circuits)}] {ckt:16s} config={nbit:6d}bit  {mark:10s} checks={nchk:4d} ({dt}s)",
          flush=True)
    with open(os.path.join(OUTD, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["circuit", "config_bit", "simulation", "checks", "sec"])
        w.writerows(rows)

ok = sum(1 for r in rows if r[2] == "PASS")
print(f"\n=== シミュレーション一致 {ok}/{len(rows)}  ({round(time.time()-t0)}s) ===")
print(f"出力: {os.path.join(OUTD, 'summary.csv')}")
for r in rows:
    if r[2] != "PASS":
        print(f"  要確認: {r[0]} -> {r[2]}  ログ: {os.path.join(OUTD, r[0], 'sim.log')}")
