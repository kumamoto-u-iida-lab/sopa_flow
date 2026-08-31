module dmac ( clk,
	rst,
	x1,
	x2,
	x3,
	x4,
	x5,
	x6,
	x7,
	x8,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23, s24=24, s25=25, s26=26, s27=27, s28=28, s29=29, s30=30;

output reg [4:0] pr_state;
reg [4:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8)
	begin
		case ( pr_state )
				s1 : if( x7 )
						nx_state = s1;
					else if( ~x7 && x6 )
						begin
							nx_state = s2;
						end
					else if( ~x7 && ~x6 )
						nx_state = s1;
					else nx_state = s1;
				s2 : if( x5 )
						nx_state = s2;
					else if( ~x5 && x3 && x2 && x1 )
						begin
							nx_state = s3;
						end
					else if( ~x5 && x3 && x2 && ~x1 )
						begin
							nx_state = s4;
						end
					else if( ~x5 && x3 && ~x2 && x1 )
						begin
							nx_state = s5;
						end
					else if( ~x5 && x3 && ~x2 && ~x1 )
						begin
							nx_state = s6;
						end
					else if( ~x5 && ~x3 && x2 && x1 )
						begin
							nx_state = s7;
						end
					else if( ~x5 && ~x3 && x2 && ~x1 )
						begin
							nx_state = s8;
						end
					else if( ~x5 && ~x3 && ~x2 && x1 )
						begin
							nx_state = s9;
						end
					else if( ~x5 && ~x3 && ~x2 && ~x1 )
						begin
							nx_state = s10;
						end
					else nx_state = s2;
				s3 : if( x8 )
						begin
							nx_state = s11;
						end
					else if( ~x8 )
						nx_state = s3;
					else nx_state = s3;
				s4 : if( x8 )
						begin
							nx_state = s12;
						end
					else if( ~x8 )
						nx_state = s4;
					else nx_state = s4;
				s5 : if( x8 )
						begin
							nx_state = s13;
						end
					else if( ~x8 )
						nx_state = s5;
					else nx_state = s5;
				s6 : if( x8 && x4 && x5 )
						begin
							nx_state = s2;
						end
					else if( x8 && x4 && ~x5 )
						begin
							nx_state = s14;
						end
					else if( x8 && ~x4 )
						begin
							nx_state = s1;
						end
					else if( ~x8 )
						nx_state = s6;
					else nx_state = s6;
				s7 : if( 1'b1 )
						begin
							nx_state = s15;
						end
					else nx_state = s7;
				s8 : if( 1'b1 )
						begin
							nx_state = s16;
						end
					else nx_state = s8;
				s9 : if( 1'b1 )
						begin
							nx_state = s17;
						end
					else nx_state = s9;
				s10 : if( x8 && x5 && x7 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x7 )
						begin
							nx_state = s2;
						end
					else if( x8 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x8 )
						nx_state = s10;
					else nx_state = s10;
				s11 : if( 1'b1 )
						begin
							nx_state = s19;
						end
					else nx_state = s11;
				s12 : if( 1'b1 )
						begin
							nx_state = s20;
						end
					else nx_state = s12;
				s13 : if( 1'b1 )
						begin
							nx_state = s21;
						end
					else nx_state = s13;
				s14 : if( x2 && x1 )
						begin
							nx_state = s3;
						end
					else if( x2 && ~x1 )
						begin
							nx_state = s4;
						end
					else if( ~x2 && x1 )
						begin
							nx_state = s5;
						end
					else if( ~x2 && ~x1 )
						begin
							nx_state = s6;
						end
					else nx_state = s14;
				s15 : if( 1'b1 )
						begin
							nx_state = s22;
						end
					else nx_state = s15;
				s16 : if( 1'b1 )
						begin
							nx_state = s23;
						end
					else nx_state = s16;
				s17 : if( 1'b1 )
						begin
							nx_state = s24;
						end
					else nx_state = s17;
				s18 : if( x2 && x1 )
						begin
							nx_state = s7;
						end
					else if( x2 && ~x1 )
						begin
							nx_state = s8;
						end
					else if( ~x2 && x1 )
						begin
							nx_state = s9;
						end
					else if( ~x2 && ~x1 )
						begin
							nx_state = s10;
						end
					else nx_state = s18;
				s19 : if( 1'b1 )
						begin
							nx_state = s21;
						end
					else nx_state = s19;
				s20 : if( x8 )
						begin
							nx_state = s25;
						end
					else if( ~x8 )
						nx_state = s20;
					else nx_state = s20;
				s21 : if( x4 && x5 )
						begin
							nx_state = s2;
						end
					else if( x4 && ~x5 )
						begin
							nx_state = s14;
						end
					else if( ~x4 )
						begin
							nx_state = s1;
						end
					else nx_state = s21;
				s22 : if( 1'b1 )
						begin
							nx_state = s26;
						end
					else nx_state = s22;
				s23 : if( 1'b1 )
						begin
							nx_state = s27;
						end
					else nx_state = s23;
				s24 : if( x8 && x5 && x7 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x7 )
						begin
							nx_state = s2;
						end
					else if( x8 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x8 )
						nx_state = s24;
					else nx_state = s24;
				s25 : if( 1'b1 )
						begin
							nx_state = s28;
						end
					else nx_state = s25;
				s26 : if( x8 && x5 && x7 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x7 )
						begin
							nx_state = s2;
						end
					else if( x8 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x8 )
						nx_state = s26;
					else nx_state = s26;
				s27 : if( x8 )
						begin
							nx_state = s29;
						end
					else if( ~x8 )
						nx_state = s27;
					else nx_state = s27;
				s28 : if( 1'b1 )
						begin
							nx_state = s21;
						end
					else nx_state = s28;
				s29 : if( 1'b1 )
						begin
							nx_state = s30;
						end
					else nx_state = s29;
				s30 : if( x8 && x5 && x7 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x7 )
						begin
							nx_state = s2;
						end
					else if( x8 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x8 )
						nx_state = s30;
					else nx_state = s30;

			default : nx_state = 0;
		endcase
	end
endmodule
