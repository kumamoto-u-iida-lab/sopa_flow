module e6 ( clk,
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
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11;

output reg [3:0] pr_state;
reg [3:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8 or x9 or x10 or x11)
	begin
		case ( pr_state )
				s1 : if( x9 && x11 && x1 && x5 )
						begin
							nx_state = s2;
						end
					else if( x9 && x11 && x1 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( x9 && x11 && ~x1 )
						begin
							nx_state = s4;
						end
					else if( x9 && ~x11 && x7 )
						begin
							nx_state = s2;
						end
					else if( x9 && ~x11 && ~x7 && x1 && x5 )
						begin
							nx_state = s2;
						end
					else if( x9 && ~x11 && ~x7 && x1 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( x9 && ~x11 && ~x7 && ~x1 )
						begin
							nx_state = s4;
						end
					else if( ~x9 && x10 && x11 && x8 )
						begin
							nx_state = s2;
						end
					else if( ~x9 && x10 && x11 && ~x8 && x5 )
						begin
							nx_state = s2;
						end
					else if( ~x9 && x10 && x11 && ~x8 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && x10 && ~x11 && x5 )
						begin
							nx_state = s5;
						end
					else if( ~x9 && x10 && ~x11 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && x1 && x11 && x3 && x6 )
						begin
							nx_state = s6;
						end
					else if( ~x9 && ~x10 && x1 && x11 && x3 && ~x6 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && x1 && x11 && ~x3 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && x1 && ~x11 && x5 )
						begin
							nx_state = s7;
						end
					else if( ~x9 && ~x10 && x1 && ~x11 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && ~x1 )
						begin
							nx_state = s4;
						end
					else nx_state = s1;
				s2 : if( 1'b1 )
						begin
							nx_state = s8;
						end
					else nx_state = s2;
				s3 : if( x4 && x9 )
						begin
							nx_state = s9;
						end
					else if( x4 && ~x9 && x10 && x11 )
						begin
							nx_state = s9;
						end
					else if( x4 && ~x9 && x10 && ~x11 && x3 )
						begin
							nx_state = s5;
						end
					else if( x4 && ~x9 && x10 && ~x11 && ~x3 )
						begin
							nx_state = s9;
						end
					else if( x4 && ~x9 && ~x10 && x3 && x11 )
						begin
							nx_state = s10;
						end
					else if( x4 && ~x9 && ~x10 && x3 && ~x11 )
						begin
							nx_state = s7;
						end
					else if( x4 && ~x9 && ~x10 && ~x3 )
						begin
							nx_state = s9;
						end
					else if( ~x4 )
						nx_state = s3;
					else nx_state = s3;
				s4 : if( x2 )
						begin
							nx_state = s11;
						end
					else if( ~x2 )
						nx_state = s4;
					else nx_state = s4;
				s5 : if( x2 )
						begin
							nx_state = s10;
						end
					else if( ~x2 )
						nx_state = s5;
					else nx_state = s5;
				s6 : if( x4 )
						begin
							nx_state = s2;
						end
					else if( ~x4 )
						nx_state = s6;
					else nx_state = s6;
				s7 : if( x2 && x6 )
						begin
							nx_state = s6;
						end
					else if( x2 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( ~x2 )
						nx_state = s7;
					else nx_state = s7;
				s8 : if( x4 )
						begin
							nx_state = s1;
						end
					else if( ~x4 )
						nx_state = s8;
					else nx_state = s8;
				s9 : if( x9 && x5 )
						begin
							nx_state = s2;
						end
					else if( x9 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && x10 && x5 && x11 )
						begin
							nx_state = s2;
						end
					else if( ~x9 && x10 && x5 && ~x11 )
						begin
							nx_state = s5;
						end
					else if( ~x9 && x10 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && x11 && x3 && x6 )
						begin
							nx_state = s6;
						end
					else if( ~x9 && ~x10 && x11 && x3 && ~x6 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && x11 && ~x3 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x10 && ~x11 && x5 )
						begin
							nx_state = s7;
						end
					else if( ~x9 && ~x10 && ~x11 && ~x5 )
						begin
							nx_state = s3;
						end
					else nx_state = s9;
				s10 : if( 1'b1 )
						begin
							nx_state = s2;
						end
					else nx_state = s10;
				s11 : if( x9 && x5 )
						begin
							nx_state = s2;
						end
					else if( x9 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && x11 && x3 && x6 )
						begin
							nx_state = s6;
						end
					else if( ~x9 && x11 && x3 && ~x6 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && x11 && ~x3 )
						begin
							nx_state = s3;
						end
					else if( ~x9 && ~x11 && x5 )
						begin
							nx_state = s7;
						end
					else if( ~x9 && ~x11 && ~x5 )
						begin
							nx_state = s3;
						end
					else nx_state = s11;

			default : nx_state = 0;
		endcase
	end
endmodule
