module dav ( clk,
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
	x17,
	x18,
	x19,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15,
	x16, x17, x18, x19;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23;

output reg [4:0] pr_state;
reg [4:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or x13 or x14 or x15 or 
	x16 or x17 or x18 or x19)
	begin
		case ( pr_state )
				s1 : if( x1 && x2 )
						begin
							nx_state = s2;
						end
					else if( x1 && ~x2 )
						begin
							nx_state = s3;
						end
					else if( ~x1 )
						nx_state = s1;
					else nx_state = s1;
				s2 : if( x18 )
						begin
							nx_state = s4;
						end
					else if( ~x18 )
						begin
							nx_state = s5;
						end
					else nx_state = s2;
				s3 : if( 1'b1 )
						begin
							nx_state = s6;
						end
					else nx_state = s3;
				s4 : if( x18 )
						begin
							nx_state = s7;
						end
					else if( ~x18 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x18 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x18 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x18 && ~x9 )
						nx_state = s1;
					else nx_state = s4;
				s5 : if( 1'b1 )
						begin
							nx_state = s7;
						end
					else nx_state = s5;
				s6 : if( x18 && x19 && x3 )
						begin
							nx_state = s8;
						end
					else if( x18 && x19 && ~x3 && x4 )
						begin
							nx_state = s9;
						end
					else if( x18 && x19 && ~x3 && ~x4 && x5 && x12 )
						begin
							nx_state = s10;
						end
					else if( x18 && x19 && ~x3 && ~x4 && x5 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && x12 && x11 )
						begin
							nx_state = s10;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x11 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x11 && x9 && ~x10 )
						nx_state = s1;
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x11 && ~x9 )
						nx_state = s1;
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && x10 )
						begin
							nx_state = s10;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x10 && x9 && x11 )
						begin
							nx_state = s1;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x10 && x9 && ~x11 )
						nx_state = s1;
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x10 && ~x9 )
						nx_state = s1;
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && ~x6 && x12 )
						begin
							nx_state = s10;
						end
					else if( x18 && x19 && ~x3 && ~x4 && ~x5 && ~x6 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && x17 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && ~x17 && x3 )
						begin
							nx_state = s8;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && x4 )
						begin
							nx_state = s9;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && x6 && x12 )
						begin
							nx_state = s11;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && x6 && ~x12 )
						begin
							nx_state = s12;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && x12 && x16 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && x12 && ~x16 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && x12 && ~x16 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && x12 && ~x16 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && x12 && ~x16 && ~x9 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && ~x12 && x15 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && ~x12 && ~x15 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && ~x12 && ~x15 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && ~x12 && ~x15 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && x5 && ~x6 && ~x12 && ~x15 && ~x9 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && x12 && x14 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x14 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x14 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x14 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && x12 && ~x14 && ~x9 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && x13 )
						begin
							nx_state = s10;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && x6 && ~x12 && ~x13 && ~x9 )
						nx_state = s1;
					else if( x18 && ~x19 && ~x17 && ~x3 && ~x4 && ~x5 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && x19 && x6 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && x19 && x6 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && x19 && ~x6 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && x19 && ~x6 && ~x12 && x3 )
						begin
							nx_state = s8;
						end
					else if( ~x18 && x5 && x19 && ~x6 && ~x12 && ~x3 && x4 )
						begin
							nx_state = s9;
						end
					else if( ~x18 && x5 && x19 && ~x6 && ~x12 && ~x3 && ~x4 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && ~x19 && x3 )
						begin
							nx_state = s8;
						end
					else if( ~x18 && x5 && ~x19 && ~x3 && x4 )
						begin
							nx_state = s9;
						end
					else if( ~x18 && x5 && ~x19 && ~x3 && ~x4 && x6 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x5 && ~x19 && ~x3 && ~x4 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x5 && x3 )
						begin
							nx_state = s8;
						end
					else if( ~x18 && ~x5 && ~x3 && x4 )
						begin
							nx_state = s9;
						end
					else if( ~x18 && ~x5 && ~x3 && ~x4 && x19 && x6 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x5 && ~x3 && ~x4 && x19 && x6 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x5 && ~x3 && ~x4 && x19 && ~x6 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x5 && ~x3 && ~x4 && x19 && ~x6 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x5 && ~x3 && ~x4 && ~x19 )
						begin
							nx_state = s10;
						end
					else nx_state = s6;
				s7 : if( 1'b1 )
						begin
							nx_state = s10;
						end
					else nx_state = s7;
				s8 : if( 1'b1 )
						begin
							nx_state = s13;
						end
					else nx_state = s8;
				s9 : if( x5 && x19 && x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( x5 && x19 && x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x5 && x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x5 && ~x19 && x6 && x18 && x12 )
						begin
							nx_state = s14;
						end
					else if( x5 && ~x19 && x6 && x18 && ~x12 )
						begin
							nx_state = s15;
						end
					else if( x5 && ~x19 && x6 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x5 && ~x19 && ~x6 && x18 && x12 && x16 )
						begin
							nx_state = s10;
						end
					else if( x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && ~x9 )
						nx_state = s1;
					else if( x5 && ~x19 && ~x6 && x18 && ~x12 && x15 )
						begin
							nx_state = s10;
						end
					else if( x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && ~x9 )
						nx_state = s1;
					else if( x5 && ~x19 && ~x6 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( ~x5 && x19 && x6 && x18 && x12 && x11 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && ~x10 )
						nx_state = s1;
					else if( ~x5 && x19 && x6 && x18 && x12 && ~x11 && ~x9 )
						nx_state = s1;
					else if( ~x5 && x19 && x6 && x18 && ~x12 && x10 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && ~x11 )
						nx_state = s1;
					else if( ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && ~x9 )
						nx_state = s1;
					else if( ~x5 && x19 && x6 && ~x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && x19 && x6 && ~x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && x19 && ~x6 && x12 && x18 )
						begin
							nx_state = s16;
						end
					else if( ~x5 && x19 && ~x6 && x12 && ~x18 )
						begin
							nx_state = s17;
						end
					else if( ~x5 && x19 && ~x6 && ~x12 && x18 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && x19 && ~x6 && ~x12 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( ~x5 && ~x19 && x18 && x6 && x12 && x14 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && ~x9 )
						nx_state = s1;
					else if( ~x5 && ~x19 && x18 && x6 && ~x12 && x13 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && ~x9 )
						nx_state = s1;
					else if( ~x5 && ~x19 && x18 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( ~x5 && ~x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else nx_state = s9;
				s10 : if( x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x9 )
						nx_state = s1;
					else nx_state = s10;
				s11 : if( x13 )
						begin
							nx_state = s10;
						end
					else if( ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x13 && ~x9 )
						nx_state = s1;
					else nx_state = s11;
				s12 : if( 1'b1 )
						begin
							nx_state = s18;
						end
					else nx_state = s12;
				s13 : if( x7 && x19 && x5 && x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && x5 && x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && x5 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && x6 && x18 && x12 && x11 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && x6 && x18 && x12 && ~x11 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x7 && x19 && ~x5 && x6 && x18 && x12 && ~x11 && x9 && ~x10 )
						nx_state = s1;
					else if( x7 && x19 && ~x5 && x6 && x18 && x12 && ~x11 && ~x9 )
						nx_state = s1;
					else if( x7 && x19 && ~x5 && x6 && x18 && ~x12 && x10 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && x6 && x18 && ~x12 && ~x10 && x9 && x11 )
						begin
							nx_state = s1;
						end
					else if( x7 && x19 && ~x5 && x6 && x18 && ~x12 && ~x10 && x9 && ~x11 )
						nx_state = s1;
					else if( x7 && x19 && ~x5 && x6 && x18 && ~x12 && ~x10 && ~x9 )
						nx_state = s1;
					else if( x7 && x19 && ~x5 && x6 && ~x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && x6 && ~x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && ~x6 && x12 && x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && ~x6 && x12 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && ~x6 && ~x12 && x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && x19 && ~x5 && ~x6 && ~x12 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && x5 && x6 && x18 && x12 )
						begin
							nx_state = s19;
						end
					else if( x7 && ~x19 && x5 && x6 && x18 && ~x12 )
						begin
							nx_state = s20;
						end
					else if( x7 && ~x19 && x5 && x6 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && x12 && x16 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && x12 && ~x16 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x7 && ~x19 && x5 && ~x6 && x18 && x12 && ~x16 && ~x9 )
						nx_state = s1;
					else if( x7 && ~x19 && x5 && ~x6 && x18 && ~x12 && x15 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && ~x12 && ~x15 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && x5 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x7 && ~x19 && x5 && ~x6 && x18 && ~x12 && ~x15 && ~x9 )
						nx_state = s1;
					else if( x7 && ~x19 && x5 && ~x6 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && x12 && x14 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && x12 && ~x14 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x7 && ~x19 && ~x5 && x18 && x6 && x12 && ~x14 && ~x9 )
						nx_state = s1;
					else if( x7 && ~x19 && ~x5 && x18 && x6 && ~x12 && x13 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && ~x12 && ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x7 && ~x19 && ~x5 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x7 && ~x19 && ~x5 && x18 && x6 && ~x12 && ~x13 && ~x9 )
						nx_state = s1;
					else if( x7 && ~x19 && ~x5 && x18 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( x7 && ~x19 && ~x5 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( ~x7 )
						begin
							nx_state = s21;
						end
					else nx_state = s13;
				s14 : if( x13 )
						begin
							nx_state = s10;
						end
					else if( ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x13 && ~x9 )
						nx_state = s1;
					else nx_state = s14;
				s15 : if( 1'b1 )
						begin
							nx_state = s10;
						end
					else nx_state = s15;
				s16 : if( x18 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && x19 )
						begin
							nx_state = s10;
						end
					else if( ~x18 && ~x19 )
						begin
							nx_state = s17;
						end
					else nx_state = s16;
				s17 : if( 1'b1 )
						begin
							nx_state = s4;
						end
					else nx_state = s17;
				s18 : if( 1'b1 )
						begin
							nx_state = s10;
						end
					else nx_state = s18;
				s19 : if( x13 )
						begin
							nx_state = s10;
						end
					else if( ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x13 && ~x9 )
						nx_state = s1;
					else nx_state = s19;
				s20 : if( 1'b1 )
						begin
							nx_state = s22;
						end
					else nx_state = s20;
				s21 : if( x4 )
						begin
							nx_state = s23;
						end
					else if( ~x4 && x8 && x5 && x19 && x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && x19 && x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && ~x19 && x6 && x18 && x12 )
						begin
							nx_state = s14;
						end
					else if( ~x4 && x8 && x5 && ~x19 && x6 && x18 && ~x12 )
						begin
							nx_state = s15;
						end
					else if( ~x4 && x8 && x5 && ~x19 && x6 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && x12 && x16 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && x15 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && x5 && ~x19 && ~x6 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && x12 && x11 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && ~x10 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && ~x12 && x10 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && ~x11 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && x19 && x6 && ~x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && x19 && x6 && ~x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && x19 && ~x6 && x12 && x18 )
						begin
							nx_state = s16;
						end
					else if( ~x4 && x8 && ~x5 && x19 && ~x6 && x12 && ~x18 )
						begin
							nx_state = s17;
						end
					else if( ~x4 && x8 && ~x5 && x19 && ~x6 && ~x12 && x18 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && x19 && ~x6 && ~x12 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && x12 && x14 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && x13 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && ~x9 )
						nx_state = s1;
					else if( ~x4 && x8 && ~x5 && ~x19 && x18 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && x8 && ~x5 && ~x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( ~x4 && ~x8 )
						begin
							nx_state = s9;
						end
					else nx_state = s21;
				s22 : if( 1'b1 )
						begin
							nx_state = s10;
						end
					else nx_state = s22;
				s23 : if( x8 && x5 && x19 && x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && x19 && x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && ~x19 && x6 && x18 && x12 )
						begin
							nx_state = s14;
						end
					else if( x8 && x5 && ~x19 && x6 && x18 && ~x12 )
						begin
							nx_state = s15;
						end
					else if( x8 && x5 && ~x19 && x6 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && x12 && x16 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x8 && x5 && ~x19 && ~x6 && x18 && x12 && ~x16 && ~x9 )
						nx_state = s1;
					else if( x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && x15 )
						begin
							nx_state = s10;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x8 && x5 && ~x19 && ~x6 && x18 && ~x12 && ~x15 && ~x9 )
						nx_state = s1;
					else if( x8 && x5 && ~x19 && ~x6 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( x8 && ~x5 && x19 && x6 && x18 && x12 && x11 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && x9 && ~x10 )
						nx_state = s1;
					else if( x8 && ~x5 && x19 && x6 && x18 && x12 && ~x11 && ~x9 )
						nx_state = s1;
					else if( x8 && ~x5 && x19 && x6 && x18 && ~x12 && x10 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && x11 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && x9 && ~x11 )
						nx_state = s1;
					else if( x8 && ~x5 && x19 && x6 && x18 && ~x12 && ~x10 && ~x9 )
						nx_state = s1;
					else if( x8 && ~x5 && x19 && x6 && ~x18 && x12 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && x19 && x6 && ~x18 && ~x12 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && x19 && ~x6 && x12 && x18 )
						begin
							nx_state = s16;
						end
					else if( x8 && ~x5 && x19 && ~x6 && x12 && ~x18 )
						begin
							nx_state = s17;
						end
					else if( x8 && ~x5 && x19 && ~x6 && ~x12 && x18 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && x19 && ~x6 && ~x12 && ~x18 )
						begin
							nx_state = s16;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && x12 && x14 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x8 && ~x5 && ~x19 && x18 && x6 && x12 && ~x14 && ~x9 )
						nx_state = s1;
					else if( x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && x13 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && x10 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && x11 )
						begin
							nx_state = s1;
						end
					else if( x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && x9 && ~x10 && ~x11 )
						nx_state = s1;
					else if( x8 && ~x5 && ~x19 && x18 && x6 && ~x12 && ~x13 && ~x9 )
						nx_state = s1;
					else if( x8 && ~x5 && ~x19 && x18 && ~x6 )
						begin
							nx_state = s10;
						end
					else if( x8 && ~x5 && ~x19 && ~x18 )
						begin
							nx_state = s10;
						end
					else if( ~x8 )
						begin
							nx_state = s9;
						end
					else nx_state = s23;

			default : nx_state = 0;
		endcase
	end
endmodule
