
module OMUX_IN051
(
  input wire CLK,
  input wire PAE_RST_N,
  input wire OMUX_I_A,
  input wire OMUX_I_B,
  input wire OMUX_I_C,
  input wire OMUX_I_D,
  input wire OMUX_I_E,
  input wire OMUX_I_F,
  input wire OMUX_I_G,
  input wire OMUX_I_H,
  input wire OMUX_I_I,
  input wire OMUX_I_J,
  input wire OMUX_I_K,
  input wire OMUX_I_L,
  input wire OMUX_I_M,
  input wire OMUX_I_N,
  input wire OMUX_I_O,
  input wire OMUX_I_P,
  input wire OMUX_I_Q,
  input wire OMUX_I_R,
  input wire OMUX_I_S,
  input wire OMUX_I_T,
  input wire OMUX_I_U,
  input wire OMUX_I_V,
  input wire OMUX_I_W,
  input wire OMUX_I_X,
  input wire OMUX_I_Y,
  input wire OMUX_I_Z,
  input wire OMUX_I_AA,
  input wire OMUX_I_AB,
  input wire OMUX_I_AC,
  input wire OMUX_I_AD,
  input wire OMUX_I_AE,
  input wire OMUX_I_AF,
  input wire OMUX_I_AG,
  input wire OMUX_I_AH,
  input wire OMUX_I_AI,
  input wire OMUX_I_AJ,
  input wire OMUX_I_AK,
  input wire OMUX_I_AL,
  input wire OMUX_I_AM,
  input wire OMUX_I_AN,
  input wire OMUX_I_AO,
  input wire OMUX_I_AP,
  input wire OMUX_I_AQ,
  input wire OMUX_I_AR,
  input wire OMUX_I_AS,
  input wire OMUX_I_AT,
  input wire OMUX_I_AU,
  input wire OMUX_I_AV,
  input wire OMUX_I_AW,
  input wire OMUX_I_AX,
  input wire OMUX_I_AY,
  output reg OMUX_O,
  input wire [6:0] PROG_DATA
);

  reg r_o;
  reg r_muxed;
  localparam MODE_MSB = 6;

  always @(*) begin
    case(PROG_DATA[5:0])
      6'd0: r_muxed = OMUX_I_A;
      6'd1: r_muxed = OMUX_I_B;
      6'd2: r_muxed = OMUX_I_C;
      6'd3: r_muxed = OMUX_I_D;
      6'd4: r_muxed = OMUX_I_E;
      6'd5: r_muxed = OMUX_I_F;
      6'd6: r_muxed = OMUX_I_G;
      6'd7: r_muxed = OMUX_I_H;
      6'd8: r_muxed = OMUX_I_I;
      6'd9: r_muxed = OMUX_I_J;
      6'd10: r_muxed = OMUX_I_K;
      6'd11: r_muxed = OMUX_I_L;
      6'd12: r_muxed = OMUX_I_M;
      6'd13: r_muxed = OMUX_I_N;
      6'd14: r_muxed = OMUX_I_O;
      6'd15: r_muxed = OMUX_I_P;
      6'd16: r_muxed = OMUX_I_Q;
      6'd17: r_muxed = OMUX_I_R;
      6'd18: r_muxed = OMUX_I_S;
      6'd19: r_muxed = OMUX_I_T;
      6'd20: r_muxed = OMUX_I_U;
      6'd21: r_muxed = OMUX_I_V;
      6'd22: r_muxed = OMUX_I_W;
      6'd23: r_muxed = OMUX_I_X;
      6'd24: r_muxed = OMUX_I_Y;
      6'd25: r_muxed = OMUX_I_Z;
      6'd26: r_muxed = OMUX_I_AA;
      6'd27: r_muxed = OMUX_I_AB;
      6'd28: r_muxed = OMUX_I_AC;
      6'd29: r_muxed = OMUX_I_AD;
      6'd30: r_muxed = OMUX_I_AE;
      6'd31: r_muxed = OMUX_I_AF;
      6'd32: r_muxed = OMUX_I_AG;
      6'd33: r_muxed = OMUX_I_AH;
      6'd34: r_muxed = OMUX_I_AI;
      6'd35: r_muxed = OMUX_I_AJ;
      6'd36: r_muxed = OMUX_I_AK;
      6'd37: r_muxed = OMUX_I_AL;
      6'd38: r_muxed = OMUX_I_AM;
      6'd39: r_muxed = OMUX_I_AN;
      6'd40: r_muxed = OMUX_I_AO;
      6'd41: r_muxed = OMUX_I_AP;
      6'd42: r_muxed = OMUX_I_AQ;
      6'd43: r_muxed = OMUX_I_AR;
      6'd44: r_muxed = OMUX_I_AS;
      6'd45: r_muxed = OMUX_I_AT;
      6'd46: r_muxed = OMUX_I_AU;
      6'd47: r_muxed = OMUX_I_AV;
      6'd48: r_muxed = OMUX_I_AW;
      6'd49: r_muxed = OMUX_I_AX;
      6'd50: r_muxed = OMUX_I_AY;
      default: r_muxed = 1'bx;
    endcase
  end


  always @(posedge CLK or negedge PAE_RST_N) begin
    if(~PAE_RST_N) r_o <= 1'b0; 
    else r_o <= r_muxed;
  end


  always @(*) begin
    if(PROG_DATA[MODE_MSB:MODE_MSB]) OMUX_O = r_muxed; 
    else OMUX_O = r_o;
  end


endmodule
