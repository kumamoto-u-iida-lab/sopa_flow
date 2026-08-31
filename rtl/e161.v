module e161 ( clk,
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
	x16,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15,
	x16;

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

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or x13 or x14 or x15 or 
	x16)
	begin
		case ( pr_state )
				s1 : if( x7 && x9 && x5 && x3 && x6 )
						begin
							nx_state = s2;
						end
					else if( x7 && x9 && x5 && x3 && ~x6 )
						begin
							nx_state = s3;
						end
					else if( x7 && x9 && x5 && ~x3 )
						begin
							nx_state = s3;
						end
					else if( x7 && x9 && ~x5 )
						begin
							nx_state = s4;
						end
					else if( x7 && ~x9 )
						begin
							nx_state = s5;
						end
					else if( ~x7 && x1 && x15 && x5 )
						begin
							nx_state = s6;
						end
					else if( ~x7 && x1 && x15 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x7 && x1 && ~x15 )
						begin
							nx_state = s4;
						end
					else if( ~x7 && ~x1 && x8 )
						begin
							nx_state = s4;
						end
					else if( ~x7 && ~x1 && ~x8 && x2 )
						begin
							nx_state = s7;
						end
					else if( ~x7 && ~x1 && ~x8 && ~x2 )
						begin
							nx_state = s7;
						end
					else nx_state = s1;
				s2 : if( x12 )
						begin
							nx_state = s8;
						end
					else if( ~x12 )
						nx_state = s2;
					else nx_state = s2;
				s3 : if( x13 && x6 && x10 && x16 )
						begin
							nx_state = s9;
						end
					else if( x13 && x6 && x10 && ~x16 )
						begin
							nx_state = s7;
						end
					else if( x13 && x6 && ~x10 )
						nx_state = s3;
					else if( x13 && ~x6 )
						nx_state = s1;
					else if( ~x13 && x15 && x4 && x10 )
						begin
							nx_state = s5;
						end
					else if( ~x13 && x15 && x4 && ~x10 )
						begin
							nx_state = s7;
						end
					else if( ~x13 && x15 && ~x4 )
						nx_state = s3;
					else if( ~x13 && ~x15 )
						nx_state = s1;
					else nx_state = s3;
				s4 : if( x12 && x14 )
						begin
							nx_state = s7;
						end
					else if( x12 && ~x14 )
						begin
							nx_state = s7;
						end
					else if( ~x12 )
						begin
							nx_state = s7;
						end
					else nx_state = s4;
				s5 : if( x7 && x11 )
						begin
							nx_state = s4;
						end
					else if( x7 && ~x11 && x2 )
						begin
							nx_state = s7;
						end
					else if( x7 && ~x11 && ~x2 )
						begin
							nx_state = s7;
						end
					else if( ~x7 && x1 && x16 )
						begin
							nx_state = s2;
						end
					else if( ~x7 && x1 && ~x16 )
						begin
							nx_state = s9;
						end
					else if( ~x7 && ~x1 )
						nx_state = s5;
					else nx_state = s5;
				s6 : if( x1 && x16 )
						begin
							nx_state = s2;
						end
					else if( x1 && ~x16 )
						begin
							nx_state = s9;
						end
					else if( ~x1 )
						nx_state = s6;
					else nx_state = s6;
				s7 : if( x10 && x7 && x3 && x6 )
						begin
							nx_state = s2;
						end
					else if( x10 && x7 && x3 && ~x6 )
						begin
							nx_state = s3;
						end
					else if( x10 && x7 && ~x3 )
						begin
							nx_state = s3;
						end
					else if( x10 && ~x7 && x9 )
						begin
							nx_state = s10;
						end
					else if( x10 && ~x7 && ~x9 && x1 )
						nx_state = s1;
					else if( x10 && ~x7 && ~x9 && ~x1 )
						begin
							nx_state = s3;
						end
					else if( ~x10 && x11 && x5 )
						begin
							nx_state = s6;
						end
					else if( ~x10 && x11 && ~x5 )
						begin
							nx_state = s3;
						end
					else if( ~x10 && ~x11 && x9 )
						begin
							nx_state = s10;
						end
					else if( ~x10 && ~x11 && ~x9 && x1 )
						nx_state = s1;
					else if( ~x10 && ~x11 && ~x9 && ~x1 )
						begin
							nx_state = s3;
						end
					else nx_state = s7;
				s8 : if( 1'b1 )
						begin
							nx_state = s11;
						end
					else nx_state = s8;
				s9 : if( 1'b1 )
						begin
							nx_state = s8;
						end
					else nx_state = s9;
				s10 : if( x1 )
						nx_state = s1;
					else if( ~x1 )
						begin
							nx_state = s3;
						end
					else nx_state = s10;
				s11 : if( x4 )
						begin
							nx_state = s1;
						end
					else if( ~x4 )
						nx_state = s11;
					else nx_state = s11;

			default : nx_state = 0;
		endcase
	end
endmodule
