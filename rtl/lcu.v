module lcu ( clk,
	rst,
	x1,
	x2,
	x3,
	x4,
	x5,
	x6,
	x7,
	x8,
	x9,
	x10,
	x11,
	x12,
	x13,
	x14,
	x15,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22;

output reg [4:0] pr_state;
reg [4:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or x13 or x14 or x15)
	begin
		case ( pr_state )
				s1 : if( x15 && x1 )
						begin
							nx_state = s2;
						end
					else if( x15 && ~x1 )
						begin
							nx_state = s3;
						end
					else if( ~x15 )
						begin
							nx_state = s3;
						end
					else nx_state = s1;
				s2 : if( x15 )
						begin
							nx_state = s4;
						end
					else if( ~x15 && x5 )
						begin
							nx_state = s5;
						end
					else if( ~x15 && ~x5 )
						begin
							nx_state = s4;
						end
					else nx_state = s2;
				s3 : if( x15 )
						begin
							nx_state = s4;
						end
					else if( ~x15 && x2 && x3 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && x2 && ~x3 && x4 )
						begin
							nx_state = s7;
						end
					else if( ~x15 && x2 && ~x3 && ~x4 )
						begin
							nx_state = s2;
						end
					else if( ~x15 && ~x2 )
						nx_state = s3;
					else nx_state = s3;
				s4 : if( x15 )
						begin
							nx_state = s8;
						end
					else if( ~x15 && x2 && x3 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && x2 && ~x3 && x4 )
						begin
							nx_state = s7;
						end
					else if( ~x15 && x2 && ~x3 && ~x4 )
						begin
							nx_state = s2;
						end
					else if( ~x15 && ~x2 )
						nx_state = s4;
					else nx_state = s4;
				s5 : if( x15 )
						nx_state = s1;
					else if( ~x15 && x6 )
						begin
							nx_state = s9;
						end
					else if( ~x15 && ~x6 )
						begin
							nx_state = s8;
						end
					else nx_state = s5;
				s6 : if( x15 && x13 )
						begin
							nx_state = s10;
						end
					else if( x15 && ~x13 )
						begin
							nx_state = s11;
						end
					else if( ~x15 && x12 )
						begin
							nx_state = s11;
						end
					else if( ~x15 && ~x12 )
						nx_state = s6;
					else nx_state = s6;
				s7 : if( x15 )
						begin
							nx_state = s5;
						end
					else if( ~x15 && x6 )
						begin
							nx_state = s9;
						end
					else if( ~x15 && ~x6 )
						begin
							nx_state = s8;
						end
					else nx_state = s7;
				s8 : if( x15 )
						begin
							nx_state = s9;
						end
					else if( ~x15 && x8 )
						begin
							nx_state = s10;
						end
					else if( ~x15 && ~x8 && x9 )
						begin
							nx_state = s10;
						end
					else if( ~x15 && ~x8 && ~x9 && x10 && x6 )
						begin
							nx_state = s9;
						end
					else if( ~x15 && ~x8 && ~x9 && x10 && ~x6 )
						begin
							nx_state = s8;
						end
					else if( ~x15 && ~x8 && ~x9 && ~x10 && x11 )
						begin
							nx_state = s12;
						end
					else if( ~x15 && ~x8 && ~x9 && ~x10 && ~x11 )
						nx_state = s8;
					else nx_state = s8;
				s9 : if( x15 && x2 && x3 && x11 )
						begin
							nx_state = s13;
						end
					else if( x15 && x2 && x3 && ~x11 && x4 && x12 && x13 )
						begin
							nx_state = s14;
						end
					else if( x15 && x2 && x3 && ~x11 && x4 && x12 && ~x13 )
						nx_state = s9;
					else if( x15 && x2 && x3 && ~x11 && x4 && ~x12 )
						nx_state = s9;
					else if( x15 && x2 && x3 && ~x11 && ~x4 )
						nx_state = s9;
					else if( x15 && x2 && ~x3 && x4 && x11 )
						begin
							nx_state = s15;
						end
					else if( x15 && x2 && ~x3 && x4 && ~x11 && x12 && x13 && x14 )
						begin
							nx_state = s16;
						end
					else if( x15 && x2 && ~x3 && x4 && ~x11 && x12 && x13 && ~x14 )
						begin
							nx_state = s6;
						end
					else if( x15 && x2 && ~x3 && x4 && ~x11 && x12 && ~x13 )
						begin
							nx_state = s17;
						end
					else if( x15 && x2 && ~x3 && x4 && ~x11 && ~x12 )
						begin
							nx_state = s18;
						end
					else if( x15 && x2 && ~x3 && ~x4 && x5 && x6 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && x5 && ~x6 && x7 && x8 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && x5 && ~x6 && x7 && ~x8 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && x5 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && x5 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && x6 && x7 && x9 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && x6 && x7 && ~x9 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && x6 && ~x7 && x9 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && x6 && ~x7 && ~x9 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && ~x6 && x7 && x10 )
						begin
							nx_state = s12;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && ~x6 && x7 && ~x10 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && ~x6 && ~x7 && x10 )
						begin
							nx_state = s5;
						end
					else if( x15 && x2 && ~x3 && ~x4 && ~x5 && ~x6 && ~x7 && ~x10 )
						begin
							nx_state = s12;
						end
					else if( x15 && ~x2 )
						nx_state = s9;
					else if( ~x15 && x7 )
						begin
							nx_state = s10;
						end
					else if( ~x15 && ~x7 && x9 )
						begin
							nx_state = s10;
						end
					else if( ~x15 && ~x7 && ~x9 && x10 && x6 )
						begin
							nx_state = s9;
						end
					else if( ~x15 && ~x7 && ~x9 && x10 && ~x6 )
						begin
							nx_state = s8;
						end
					else if( ~x15 && ~x7 && ~x9 && ~x10 && x11 )
						begin
							nx_state = s12;
						end
					else if( ~x15 && ~x7 && ~x9 && ~x10 && ~x11 )
						nx_state = s9;
					else nx_state = s9;
				s10 : if( x15 )
						nx_state = s1;
					else if( ~x15 && x11 )
						begin
							nx_state = s12;
						end
					else if( ~x15 && ~x11 && x10 )
						begin
							nx_state = s14;
						end
					else if( ~x15 && ~x11 && ~x10 )
						nx_state = s10;
					else nx_state = s10;
				s11 : if( x15 )
						nx_state = s1;
					else if( ~x15 && x13 && x4 )
						begin
							nx_state = s7;
						end
					else if( ~x15 && x13 && ~x4 )
						begin
							nx_state = s2;
						end
					else if( ~x15 && ~x13 && x14 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && ~x13 && ~x14 && x9 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && x7 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && ~x7 && x8 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && ~x7 && ~x8 )
						nx_state = s11;
					else nx_state = s11;
				s12 : if( x15 )
						begin
							nx_state = s7;
						end
					else if( ~x15 )
						nx_state = s1;
					else nx_state = s12;
				s13 : if( 1'b1 )
						begin
							nx_state = s15;
						end
					else nx_state = s13;
				s14 : if( x12 && x15 && x13 && x3 )
						begin
							nx_state = s16;
						end
					else if( x12 && x15 && x13 && ~x3 && x14 )
						begin
							nx_state = s16;
						end
					else if( x12 && x15 && x13 && ~x3 && ~x14 )
						begin
							nx_state = s6;
						end
					else if( x12 && x15 && ~x13 )
						begin
							nx_state = s17;
						end
					else if( x12 && ~x15 )
						begin
							nx_state = s18;
						end
					else if( ~x12 )
						begin
							nx_state = s18;
						end
					else nx_state = s14;
				s15 : if( 1'b1 )
						begin
							nx_state = s1;
						end
					else nx_state = s15;
				s16 : if( 1'b1 )
						begin
							nx_state = s19;
						end
					else nx_state = s16;
				s17 : if( x15 && x14 )
						begin
							nx_state = s20;
						end
					else if( x15 && ~x14 )
						begin
							nx_state = s6;
						end
					else if( ~x15 && x12 )
						begin
							nx_state = s21;
						end
					else if( ~x15 && ~x12 )
						nx_state = s17;
					else nx_state = s17;
				s18 : if( x15 )
						begin
							nx_state = s21;
						end
					else if( ~x15 && x6 )
						begin
							nx_state = s20;
						end
					else if( ~x15 && ~x6 )
						begin
							nx_state = s17;
						end
					else nx_state = s18;
				s19 : if( 1'b1 )
						begin
							nx_state = s22;
						end
					else nx_state = s19;
				s20 : if( x15 )
						begin
							nx_state = s19;
						end
					else if( ~x15 && x12 )
						begin
							nx_state = s21;
						end
					else if( ~x15 && ~x12 )
						nx_state = s20;
					else nx_state = s20;
				s21 : if( x15 )
						nx_state = s1;
					else if( ~x15 && x13 && x11 )
						begin
							nx_state = s12;
						end
					else if( ~x15 && x13 && ~x11 && x6 && x4 )
						begin
							nx_state = s7;
						end
					else if( ~x15 && x13 && ~x11 && x6 && ~x4 )
						begin
							nx_state = s2;
						end
					else if( ~x15 && x13 && ~x11 && ~x6 && x5 )
						begin
							nx_state = s5;
						end
					else if( ~x15 && x13 && ~x11 && ~x6 && ~x5 )
						begin
							nx_state = s4;
						end
					else if( ~x15 && ~x13 && x14 )
						begin
							nx_state = s18;
						end
					else if( ~x15 && ~x13 && ~x14 && x9 )
						begin
							nx_state = s18;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && x6 && x2 )
						begin
							nx_state = s18;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && x6 && ~x2 )
						nx_state = s21;
					else if( ~x15 && ~x13 && ~x14 && ~x9 && ~x6 && x8 )
						begin
							nx_state = s18;
						end
					else if( ~x15 && ~x13 && ~x14 && ~x9 && ~x6 && ~x8 )
						nx_state = s21;
					else nx_state = s21;
				s22 : if( x14 && x13 )
						begin
							nx_state = s1;
						end
					else if( x14 && ~x13 )
						begin
							nx_state = s21;
						end
					else if( ~x14 )
						begin
							nx_state = s10;
						end
					else nx_state = s22;

			default : nx_state = 0;
		endcase
	end
endmodule
