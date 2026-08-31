#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_tb_sopa.py — Ref(元RTL) と Impl(SoPA) を同一tbに並べ、毎サイクル出力を自動照合するtbを作る。

案A: CONFIG_DATA は Impl の外部ポート。tb が <回路>.bit を $readmemb で読んで与える
     (案Bに移ったら、この与え方を CONF_IN のシリアル書き込みに差し替える)。

 使い方: python3 gen_tb_sopa.py <IMPL_V> [-n パターン数] [-o 出力tb]
   IMPL_V は CFGPORT=1 で作った impl_<回路>.v。Ref RTL は RTL_DIR から <回路>.v を探す。
 環境変数: RTL_DIR (既定 state_benchmark/state_Small_no_dec/Verilog)
"""
import sys, os, re, argparse

SD = os.path.dirname(os.path.abspath(__file__))
FF1 = os.path.dirname(SD)
RTL_DIR = os.environ.get("RTL_DIR", os.path.join(FF1, "state_benchmark", "state_Small_no_dec", "Verilog"))

TB = """`timescale 1ns / 1ps
// {ckt}: Ref(元RTL) vs Impl(SoPA構造+bitstream) 同時照合テストベンチ  [案A: CONFIG_DATAは並列ポート]
//   Ref  = {refv}
//   Impl = {implv}   CONFIG={nbit}bit  <- {bit}
module tb_{ckt};
  parameter P = 10;              // クロック周期
  parameter NPAT = {npat};           // 印加パターン数
  parameter NBIT = {nbit};

  reg clk, rst;
  reg {pi_decl};
  wire {ref_decl};
  wire {impl_decl};

  reg [NBIT-1:0] cfg_mem [0:0];
  reg [NBIT-1:0] config_data;
{ser_decl}
  integer i, errors, checks;

  // ---- DUT: 元RTL(Ref) ----
  {refmod} u_ref (
{ref_conn}
  );

  // ---- DUT: SoPA実装(Impl) ----
  {ckt}_impl u_impl (
{impl_conn}
  );

  // ---- クロック ----
  initial begin clk = 1'b0; forever #(P/2) clk = ~clk; end

  // ---- bitstream ロード(案A: 並列に与えるだけ) ----
  initial begin
    $readmemb("{bit}", cfg_mem);
    config_data = cfg_mem[0];
    if (^config_data === 1'bx) begin
      $display("FATAL: bitstream の読み込みに失敗 ({bit})");
      $finish;
    end
    $display("Configuration loaded: %0d bits", NBIT);
  end

  // ---- 照合 ----
  task check;
    begin
      checks = checks + 1;
      if ({cmp}) begin
        errors = errors + 1;
        if (errors <= 10)
          $display("  MISMATCH t=%0t  in={{{pi_list}}}=%b  ref=%b  impl=%b",
                   $time, {{{pi_list}}}, {ref_cat}, {impl_cat});
      end
    end
  endtask

  initial begin
    errors = 0; checks = 0;
    {pi_init}
{ser_load}
    // 1) リセット (元RTLは rst==1 でリセット)
    rst = 1'b1;
    repeat (4) @(posedge clk);
    #1 rst = 1'b0;
    @(posedge clk);
    check;                       // リセット直後の状態も照合する

    // 2) ランダムパターン印加。入力は posedge で変え、状態更新(negedge)を跨いでから照合する
    for (i = 0; i < NPAT; i = i + 1) begin
      @(posedge clk);
      #1 {pi_rand}
      @(posedge clk);
      #1 check;
    end

    $display("========================================");
    if (errors == 0) $display("[PASS] {ckt}: %0d checks all match (Ref == Impl)", checks);
    else             $display("[FAIL] {ckt}: %0d / %0d checks mismatched", errors, checks);
    $display("========================================");
    $finish;
  end

  initial begin
    $dumpfile("tb_{ckt}.vcd");
    $dumpvars(0, tb_{ckt});
  end
endmodule
"""


SER_DECL = """
  // 案B: 既存eFPGAと同じシリアル書き込み口
  reg CONF_CLK, CONF_RESETL, CONF_MODE, CONF_IN, CONF_E;
  wire CONF_OUT;
  integer j, bad;
  parameter CONF_CLK_PERIOD = 10;
"""

SER_LOAD = """    // ---- bitstream を CONF_IN から1bitずつ流し込む(先輩tbと同じ手順) ----
    CONF_CLK = 1'b0; CONF_RESETL = 1'b0; CONF_MODE = 1'b0; CONF_IN = 1'b0; CONF_E = 1'b0;
    #100;
    $display("[%0t] Step 1: Configuration Reset", $time);
    CONF_RESETL = 1'b0; #(CONF_CLK_PERIOD*5); CONF_RESETL = 1'b1; #(CONF_CLK_PERIOD*2);

    $display("[%0t] Step 2: Loading Configuration Data (%0d bits)", $time, NBIT);
    CONF_MODE = 1'b1; CONF_E = 1'b0;
    for (j = 0; j < NBIT; j = j + 1) begin
      CONF_IN = config_data[NBIT-1-j];        // MSBから送る
      #1; CONF_CLK = 1'b1; #(CONF_CLK_PERIOD/2);
          CONF_CLK = 1'b0; #(CONF_CLK_PERIOD/2 - 1);
    end
    CONF_MODE = 1'b0; CONF_IN = 1'b0;

    $display("[%0t] Step 3: Verifying Configuration Data", $time);
    CONF_E = 1'b1; #10;
    bad = 0;
    for (j = 0; j < NBIT; j = j + 1)
      if (u_impl.CONFIG_DATA[j] !== config_data[j]) begin
        if (bad < 5) $display("  CONFIG MISMATCH bit[%0d]: expected=%b actual=%b",
                              j, config_data[j], u_impl.CONFIG_DATA[j]);
        bad = bad + 1;
      end
    if (bad == 0) $display("  SUCCESS: All %0d config bits match", NBIT);
    else begin $display("  FAILED: %0d config bits mismatched", bad); errors = errors + bad; end

    $display("[%0t] Step 4: Entering Normal Operation Mode", $time);
"""


def parse_impl(path):
    """impl_<回路>.v のモジュール宣言から 回路名/入力PI/出力バス/CONFIG幅 を取り出す。"""
    txt = open(path).read()
    m = re.search(r'module\s+(\w+)_impl\s*\((.*?)\);', txt, re.S)
    if not m:
        raise ValueError(f"module <回路>_impl の宣言が見つからない: {path}")
    ckt, body = m.group(1), m.group(2)
    pis, outs, nbit = [], [], None
    for p in [s.strip() for s in body.split(',')]:
        mo = re.match(r'(input|output)\s+wire\s*(?:\[(\d+):(\d+)\])?\s*(\w+)$', p)
        if not mo:
            continue
        kind, hi, _lo, name = mo.groups()
        if name == 'CONFIG_DATA':
            nbit = int(hi) + 1
        elif name.startswith('CONF_'):     # 設定書き込み用の口。回路のデータI/Oではない
            continue
        elif kind == 'input' and name not in ('clk', 'rst'):
            pis.append(name)
        elif kind == 'output':
            outs.append((name, int(hi) if hi else None))
    serial = 'CONF_IN' in body            # 案B: シリアル書き込み口が付いているか
    if serial and nbit is None:           # 幅は CONF_SHIFT の NBIT から取る
        m2 = re.search(r'CONF_SHIFT\s*#\(\.NBIT\((\d+)\)\)', txt)
        if m2:
            nbit = int(m2.group(1))
    if nbit is None:
        raise ValueError(f"CONFIG_DATA が外部ポートになっていない。CFGPORT=1 か SERIAL=1 で生成し直す: {path}")
    return ckt, pis, outs, nbit, serial


def build(implv, npat, out=None):
    ckt, pis, outs, nbit, serial = parse_impl(implv)
    refv = os.path.join(RTL_DIR, f"{ckt}.v")
    if not os.path.isfile(refv):
        raise FileNotFoundError(f"元RTLが見つからない: {refv}")
    refmod = re.search(r'\bmodule\s+(\w+)', open(refv).read()).group(1)
    od = os.path.dirname(os.path.abspath(implv))
    ser_ports = (",\n    .CONF_CLK(CONF_CLK),\n    .CONF_RESETL(CONF_RESETL),"
                 "\n    .CONF_MODE(CONF_MODE),\n    .CONF_IN(CONF_IN),"
                 "\n    .CONF_E(CONF_E),\n    .CONF_OUT(CONF_OUT)")

    def sig(pfx, n, w):
        return f"{pfx}_{n}" + (f" [{w}:0]" if w is not None else "")
    decl = lambda pfx: ", ".join((f"[{w}:0] " if w is not None else "") + f"{pfx}_{n}" for n, w in outs)
    conn = lambda pfx: ",\n".join([f"    .clk(clk)", f"    .rst(rst)"]
                                  + [f"    .{p}({p})" for p in pis]
                                  + [f"    .{n}({pfx}_{n})" for n, _ in outs])
    txt = TB.format(
        ckt=ckt, refmod=refmod, refv=os.path.relpath(refv, od), implv=os.path.basename(implv),
        bit=f"{ckt}.bit", nbit=nbit, npat=npat,
        pi_decl=", ".join(pis),
        ref_decl=decl("ref"), impl_decl=decl("impl"),
        ref_conn=conn("ref"),
        impl_conn=conn("impl") + (ser_ports if serial else ",\n    .CONFIG_DATA(config_data)"),
        ser_decl=SER_DECL if serial else "",
        ser_load=SER_LOAD if serial else "",
        cmp=" || ".join(f"(ref_{n} !== impl_{n})" for n, _ in outs),
        pi_list=", ".join(pis),
        ref_cat="{" + ", ".join(f"ref_{n}" for n, _ in outs) + "}",
        impl_cat="{" + ", ".join(f"impl_{n}" for n, _ in outs) + "}",
        pi_init=" ".join(f"{p} = 1'b0;" for p in pis),
        pi_rand=" ".join(f"{p} = $random;" for p in pis),
    )
    out = out or os.path.join(od, f"tb_{ckt}.v")
    open(out, "w").write(txt)
    print(f"tb出力: {out}")
    print(f"  Ref  = {refv}  (module {refmod})")
    print(f"  Impl = {implv}  (module {ckt}_impl, CONFIG={nbit}bit, " + ("シリアル書き込み=案B)" if serial else "並列ポート=案A)"))
    print(f"  入力PI {len(pis)}本: {', '.join(pis)}")
    print(f"  照合出力: {', '.join(n for n, _ in outs)}   パターン数={npat}")
    print(f"\n  実行例:  vcs -full64 -sverilog {os.path.relpath(refv, od)} {os.path.basename(implv)} "
          f"<構造.v> {os.path.basename(out)} -o simv && ./simv")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("impl_v")
    ap.add_argument("-n", "--npat", type=int, default=200)
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    build(a.impl_v, a.npat, a.out)
