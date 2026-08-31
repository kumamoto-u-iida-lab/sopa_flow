module robotben ( clk,
	rst,
	x1,
	x2,
	x3,
	x4,
	x5,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23, s24=24, s25=25, s26=26, s27=27, s28=28, s29=29, s30=30,
	s31=31, s32=32, s33=33, s34=34, s35=35, s36=36, s37=37, s38=38, s39=39, s40=40,
	s41=41, s42=42, s43=43, s44=44, s45=45, s46=46, s47=47;

output reg [5:0] pr_state;
reg [5:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5)
	begin
		case ( pr_state )
				s1 : if( x4 )
						begin
							nx_state = s2;
						end
					else if( ~x4 )
						nx_state = s1;
					else nx_state = s1;
				s2 : if( 1'b1 )
						begin
							nx_state = s3;
						end
					else nx_state = s2;
				s3 : if( 1'b1 )
						begin
							nx_state = s4;
						end
					else nx_state = s3;
				s4 : if( x1 )
						begin
							nx_state = s5;
						end
					else if( ~x1 )
						begin
							nx_state = s3;
						end
					else nx_state = s4;
				s5 : if( x3 )
						begin
							nx_state = s6;
						end
					else if( ~x3 )
						nx_state = s5;
					else nx_state = s5;
				s6 : if( x3 )
						begin
							nx_state = s6;
						end
					else if( ~x3 )
						begin
							nx_state = s7;
						end
					else nx_state = s6;
				s7 : if( 1'b1 )
						begin
							nx_state = s8;
						end
					else nx_state = s7;
				s8 : if( x1 )
						begin
							nx_state = s9;
						end
					else if( ~x1 )
						begin
							nx_state = s10;
						end
					else nx_state = s8;
				s9 : if( 1'b1 )
						begin
							nx_state = s11;
						end
					else nx_state = s9;
				s10 : if( 1'b1 )
						begin
							nx_state = s12;
						end
					else nx_state = s10;
				s11 : if( 1'b1 )
						begin
							nx_state = s13;
						end
					else nx_state = s11;
				s12 : if( 1'b1 )
						begin
							nx_state = s14;
						end
					else nx_state = s12;
				s13 : if( x1 )
						begin
							nx_state = s15;
						end
					else if( ~x1 )
						begin
							nx_state = s11;
						end
					else nx_state = s13;
				s14 : if( x1 )
						begin
							nx_state = s16;
						end
					else if( ~x1 )
						begin
							nx_state = s12;
						end
					else nx_state = s14;
				s15 : if( x3 )
						begin
							nx_state = s17;
						end
					else if( ~x3 )
						nx_state = s15;
					else nx_state = s15;
				s16 : if( x2 )
						begin
							nx_state = s18;
						end
					else if( ~x2 )
						nx_state = s16;
					else nx_state = s16;
				s17 : if( x3 )
						begin
							nx_state = s17;
						end
					else if( ~x3 )
						begin
							nx_state = s19;
						end
					else nx_state = s17;
				s18 : if( x2 )
						begin
							nx_state = s18;
						end
					else if( ~x2 )
						begin
							nx_state = s20;
						end
					else nx_state = s18;
				s19 : if( 1'b1 )
						begin
							nx_state = s21;
						end
					else nx_state = s19;
				s20 : if( 1'b1 )
						begin
							nx_state = s22;
						end
					else nx_state = s20;
				s21 : if( 1'b1 )
						begin
							nx_state = s23;
						end
					else nx_state = s21;
				s22 : if( 1'b1 )
						begin
							nx_state = s24;
						end
					else nx_state = s22;
				s23 : if( x1 )
						begin
							nx_state = s25;
						end
					else if( ~x1 )
						begin
							nx_state = s26;
						end
					else nx_state = s23;
				s24 : if( 1'b1 )
						begin
							nx_state = s27;
						end
					else nx_state = s24;
				s25 : if( 1'b1 )
						begin
							nx_state = s28;
						end
					else nx_state = s25;
				s26 : if( x1 )
						begin
							nx_state = s25;
						end
					else if( ~x1 )
						begin
							nx_state = s29;
						end
					else nx_state = s26;
				s27 : if( 1'b1 )
						begin
							nx_state = s30;
						end
					else nx_state = s27;
				s28 : if( 1'b1 )
						begin
							nx_state = s31;
						end
					else nx_state = s28;
				s29 : if( x1 )
						begin
							nx_state = s25;
						end
					else if( ~x1 )
						begin
							nx_state = s32;
						end
					else nx_state = s29;
				s30 : if( x1 )
						begin
							nx_state = s33;
						end
					else if( ~x1 )
						begin
							nx_state = s34;
						end
					else nx_state = s30;
				s31 : if( x1 )
						begin
							nx_state = s35;
						end
					else if( ~x1 )
						begin
							nx_state = s36;
						end
					else nx_state = s31;
				s32 : if( x5 )
						begin
							nx_state = s1;
						end
					else if( ~x5 )
						begin
							nx_state = s9;
						end
					else nx_state = s32;
				s33 : if( 1'b1 )
						begin
							nx_state = s37;
						end
					else nx_state = s33;
				s34 : if( 1'b1 )
						begin
							nx_state = s33;
						end
					else nx_state = s34;
				s35 : if( 1'b1 )
						begin
							nx_state = s38;
						end
					else nx_state = s35;
				s36 : if( 1'b1 )
						begin
							nx_state = s35;
						end
					else nx_state = s36;
				s37 : if( x1 )
						begin
							nx_state = s30;
						end
					else if( ~x1 )
						begin
							nx_state = s39;
						end
					else nx_state = s37;
				s38 : if( x1 )
						begin
							nx_state = s31;
						end
					else if( ~x1 && x5 )
						begin
							nx_state = s1;
						end
					else if( ~x1 && ~x5 )
						begin
							nx_state = s9;
						end
					else nx_state = s38;
				s39 : if( 1'b1 )
						begin
							nx_state = s40;
						end
					else nx_state = s39;
				s40 : if( 1'b1 )
						begin
							nx_state = s41;
						end
					else nx_state = s40;
				s41 : if( x1 )
						begin
							nx_state = s42;
						end
					else if( ~x1 )
						begin
							nx_state = s40;
						end
					else nx_state = s41;
				s42 : if( x2 )
						begin
							nx_state = s43;
						end
					else if( ~x2 )
						nx_state = s42;
					else nx_state = s42;
				s43 : if( x2 )
						begin
							nx_state = s43;
						end
					else if( ~x2 )
						begin
							nx_state = s44;
						end
					else nx_state = s43;
				s44 : if( 1'b1 )
						begin
							nx_state = s45;
						end
					else nx_state = s44;
				s45 : if( 1'b1 )
						begin
							nx_state = s46;
						end
					else nx_state = s45;
				s46 : if( x1 )
						begin
							nx_state = s47;
						end
					else if( ~x1 )
						begin
							nx_state = s22;
						end
					else nx_state = s46;
				s47 : if( 1'b1 )
						begin
							nx_state = s2;
						end
					else nx_state = s47;

			default : nx_state = 0;
		endcase
	end
endmodule
