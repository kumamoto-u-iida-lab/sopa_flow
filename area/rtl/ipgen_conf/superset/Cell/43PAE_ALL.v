
// Author: Ryo Iwasaki
// Date: 2025/10/07

// Description: PAE with 4 inputs and 3 outputs
// All patterns are used
// PA version is v1

module PAE (
    input wire PAE_I_A
    , input wire PAE_I_B
    , input wire PAE_I_C
    , input wire PAE_I_D
    , output wire PAE_O_A
    , output wire PAE_O_B
    , output wire PAE_O_C
    , input wire [7:0] PROG_DATA
    // PROG_DATA[ 0 +:  8] pae mode select
    );

    localparam P_PAE_MODE = 0;
    localparam P_PAE_MODE_WIDTH = 8;
   
    wire w_x1, w_y1, w_x2, w_y2, w_x3, w_y3;
    wire w_n0, w_n1, w_n2, w_n3, w_n4, w_n5;
   
    wire [P_PAE_MODE_WIDTH-1:0] w_pae_mode;
   
    assign w_pae_mode = PROG_DATA[P_PAE_MODE+:P_PAE_MODE_WIDTH];

    // -- Input muxes ---------------------------------

    assign  w_x1 = PAE_I_A;
    assign  w_y1 = (w_pae_mode[6] == 1'b0) ? PAE_O_B : PAE_I_B;
    assign  w_x2 = (w_pae_mode[6] == 1'b0) ? PAE_I_B : PAE_O_A;
    assign  w_y2 = (w_pae_mode[7] == 1'b0) ? PAE_I_C : PAE_O_C;
    assign  w_x3 = (w_pae_mode[7] == 1'b0) ? PAE_O_B : PAE_I_C;
    assign  w_y3 = PAE_I_D;

    // -- Outputs -------------------------------------

    assign w_n0 = w_y1 ^ w_pae_mode[0];
    assign w_n1 = w_x1 & w_n0;
    assign PAE_O_A = w_n1 ^ w_pae_mode[1];

    assign w_n2 = w_y2 ^ w_pae_mode[2];
    assign w_n3 = w_x2 & w_n2;
    assign PAE_O_B = w_n3 ^ w_pae_mode[3];

    assign w_n4 = w_y3 ^ w_pae_mode[4];
    assign w_n5 = w_x3 & w_n4;
    assign PAE_O_C = w_n5 ^ w_pae_mode[5];

endmodule