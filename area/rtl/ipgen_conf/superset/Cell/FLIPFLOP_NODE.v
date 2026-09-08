//******************************************************************************
// Copyright (C) 2024 MavissDesign Co.,Ltd. All rights reserved.
//******************************************************************************
//------------------------------------------------------------------------------
// Project     : KUTEG00
// Author      : H.Nishihara
// Company     : MavissDesign Co.,Ltd
//------------------------------------------------------------------------------
// Description :
//      A path selector of PAE's output signal. (FF or through)
//------------------------------------------------------------------------------
// Revision history :
// Rev    Author         Date         Comments
// -----  -------------  -----------  ------------------------------------------
// r1.00  H.Nishihara    2024/06/26   Initial version
//------------------------------------------------------------------------------

module FLIPFLOP_NODE (
    input wire CLK
    , input wire PAE_RST_N
    , input wire FFNODE_I
    , output reg FFNODE_O
    , input wire PROG_DATA
    );

    reg r_o;

    // FF for Output
    always @ (posedge CLK or negedge PAE_RST_N) begin
        if(~PAE_RST_N)
            r_o <= 1'b0;
        else
            r_o <= FFNODE_I;
    end

    // select FF or wire
    always @ (*) begin
        if(PROG_DATA)
            FFNODE_O = FFNODE_I;
        else
            FFNODE_O = r_o;
    end

endmodule