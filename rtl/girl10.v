module girl10 ( clk,
	rst,
	x1,
	x2,
	x3,
	x4,
	x5,
	x6,
	x7,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6;

output reg [2:0] pr_state;
reg [2:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7)
	begin
		case ( pr_state )
				s1 : if( x6 )
						begin
							nx_state = s2;
						end
					else if( ~x6 && x7 )
						begin
							nx_state = s3;
						end
					else if( ~x6 && ~x7 )
						begin
							nx_state = s3;
						end
					else nx_state = s1;
				s2 : if( x4 && x1 )
						begin
							nx_state = s2;
						end
					else if( x4 && ~x1 )
						begin
							nx_state = s4;
						end
					else if( ~x4 )
						begin
							nx_state = s5;
						end
					else nx_state = s2;
				s3 : if( x1 && x2 && x3 )
						begin
							nx_state = s2;
						end
					else if( x1 && x2 && ~x3 )
						begin
							nx_state = s6;
						end
					else if( x1 && ~x2 )
						begin
							nx_state = s2;
						end
					else if( ~x1 )
						begin
							nx_state = s5;
						end
					else nx_state = s3;
				s4 : if( x6 )
						begin
							nx_state = s3;
						end
					else if( ~x6 )
						begin
							nx_state = s4;
						end
					else nx_state = s4;
				s5 : if( x5 )
						nx_state = s1;
					else if( ~x5 && x1 )
						begin
							nx_state = s2;
						end
					else if( ~x5 && ~x1 )
						begin
							nx_state = s4;
						end
					else nx_state = s5;
				s6 : if( 1'b1 )
						begin
							nx_state = s4;
						end
					else nx_state = s6;

			default : nx_state = 0;
		endcase
	end
endmodule
