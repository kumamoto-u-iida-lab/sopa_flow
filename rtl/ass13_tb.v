`timescale 1ns/1ps

module ass13_tb;

reg clk, rst, x1, x2, x3, x4, x5;
wire [4:0] pr_state;

ass13 uut (
    .clk(clk), .rst(rst),
    .x1(x1), .x2(x2), .x3(x3), .x4(x4), .x5(x5),
    .pr_state(pr_state)
);

// クロック: 10ns周期
always #5 clk = ~clk;

task show;
    input [4:0] s;
    begin
        $write("  pr_state = s%0d", s);
        $display("");
    end
endtask

integer cyc;
initial begin
    clk = 0; rst = 1; x1 = 0; x2 = 0; x3 = 0; x4 = 0; x5 = 0;
    #12 rst = 0;  // リセット解除

    $display("=== ass13 FSM simulation ===");
    $display("%-5s %-8s %-5s %-5s %-5s %-5s %-5s %-10s", "Cycle", "rst", "x1","x2","x3","x4","x5", "pr_state");

    for (cyc = 0; cyc < 30; cyc = cyc + 1) begin
        // 入力をサイクルごとに変化させる
        case (cyc)
            0:  begin x4=1; x5=1; x1=1; x2=0; x3=0; end // s2 -> s3
            1:  begin x4=1; x5=1; x1=0; x2=0; x3=0; end // s3 -> s8
            2:  begin x4=1; x5=1; x1=0; x2=0; x3=0; end // s8 -> s10
            3:  begin x5=1; x4=1; x2=1; x3=0; x1=0; end // s10 -> s2
            4:  begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s2 -> s7
            5:  begin x4=1; x5=0; x1=0; x2=0; x3=0; end // s7 -> s6
            6:  begin x4=1; x5=1; x1=0; x2=0; x3=0; end // s6 -> s5
            7:  begin x5=0; x2=0; x4=0; x1=0; x3=0; end // s5 -> s14
            8:  begin x4=1; x5=0; x1=0; x2=0; x3=0; end // s14 -> s15
            9:  begin x2=0; x1=1; x4=0; x5=0; x3=0; end // s15 -> s5
            10: begin x5=1; x2=1; x4=0; x1=0; x3=0; end // s5 -> s14
            11: begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s14 -> s16
            12: begin x4=0; x2=1; x1=0; x3=0; x5=0; end // s16 -> s19
            13: begin x4=0; x2=0; x1=0; x3=0; x5=0; end // s19 -> s9
            14: begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s9 -> s11
            15: begin x4=1; x5=0; x2=0; x3=0; x1=0; end // s11 -> s3
            16: begin x1=1; x4=0; x5=0; x2=0; x3=0; end // s3 -> s8
            17: begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s8 -> s10
            18: begin x5=0; x4=0; x2=0; x1=0; x3=0; end // s10 -> s11
            19: begin x4=1; x5=0; x2=1; x3=1; x1=0; end // s11 -> s12
            20: begin x4=1; x5=0; x2=0; x3=0; x1=0; end // s12 -> s18
            21: begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s18 -> s7
            22: begin x4=1; x5=0; x1=1; x2=0; x3=0; end // s7 -> s5
            23: begin x5=1; x2=0; x4=1; x1=1; x3=0; end // s5 -> s9
            24: begin x4=1; x5=0; x2=0; x3=0; x1=0; end // s9 -> s17
            25: begin x3=1; x4=0; x5=0; x1=0; x2=0; end // s17 -> s19
            26: begin x4=0; x5=0; x1=0; x2=0; x3=0; end // s19 -> s9
            27: begin x4=1; x5=1; x1=0; x2=0; x3=0; end // s9 -> s6
            28: begin x4=1; x5=0; x2=0; x3=0; x1=0; end // s6 -> s15
            29: begin x2=1; x4=0; x5=0; x1=0; x3=0; end // s15 -> s13
        endcase

        @(negedge clk); // クロック立ち下がりでサンプル
        $display("%-5d rst=%b  x1=%b x2=%b x3=%b x4=%b x5=%b  pr_state=s%0d",
                  cyc, rst, x1, x2, x3, x4, x5, pr_state);
    end

    $display("=== simulation done ===");
    $finish;
end

endmodule
