module lior ( clk,
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
	x20,
	x21,
	x22,
	x23,
	x24,
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15,
	x16, x17, x18, x19, x20, x21, x22, x23, x24;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23, s24=24, s25=25, s26=26, s27=27, s28=28, s29=29, s30=30,
	s31=31;

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
	x16 or x17 or x18 or x19 or x20 or x21 or x22 or x23 or x24)
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
				s2 : if( 1'b1 )
						begin
							nx_state = s4;
						end
					else nx_state = s2;
				s3 : if( 1'b1 )
						begin
							nx_state = s5;
						end
					else nx_state = s3;
				s4 : if( 1'b1 )
						begin
							nx_state = s6;
						end
					else nx_state = s4;
				s5 : if( 1'b1 )
						begin
							nx_state = s7;
						end
					else nx_state = s5;
				s6 : if( 1'b1 )
						begin
							nx_state = s8;
						end
					else nx_state = s6;
				s7 : if( x3 && x24 && x23 && x7 )
						begin
							nx_state = s9;
						end
					else if( x3 && x24 && x23 && ~x7 )
						begin
							nx_state = s10;
						end
					else if( x3 && x24 && ~x23 && x5 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x3 && x24 && ~x23 && x5 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x3 && x24 && ~x23 && x5 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x3 && x24 && ~x23 && x5 && ~x20 )
						nx_state = s1;
					else if( x3 && x24 && ~x23 && ~x5 )
						begin
							nx_state = s12;
						end
					else if( x3 && ~x24 && x5 && x11 && x12 && x23 )
						begin
							nx_state = s1;
						end
					else if( x3 && ~x24 && x5 && x11 && x12 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( x3 && ~x24 && x5 && x11 && ~x12 && x13 && x23 )
						begin
							nx_state = s1;
						end
					else if( x3 && ~x24 && x5 && x11 && ~x12 && x13 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( x3 && ~x24 && x5 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( x3 && ~x24 && x5 && ~x11 )
						nx_state = s1;
					else if( x3 && ~x24 && ~x5 )
						begin
							nx_state = s12;
						end
					else if( ~x3 )
						begin
							nx_state = s14;
						end
					else nx_state = s7;
				s8 : if( x24 )
						nx_state = s1;
					else if( ~x24 && x23 && x10 )
						begin
							nx_state = s15;
						end
					else if( ~x24 && x23 && ~x10 )
						begin
							nx_state = s16;
						end
					else if( ~x24 && ~x23 )
						nx_state = s1;
					else nx_state = s8;
				s9 : if( x24 && x23 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && x23 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && x9 && x10 && x11 )
						begin
							nx_state = s18;
						end
					else if( x24 && ~x23 && x7 && x9 && x10 && ~x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && x13 && x14 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && x9 && ~x10 && x13 && ~x14 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && x9 && ~x10 && ~x13 && x15 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && x9 && ~x10 && ~x13 && ~x15 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && ~x9 && x16 && x17 && x18 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && ~x9 && x16 && x17 && ~x18 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && ~x9 && x16 && ~x17 && x19 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && ~x9 && x16 && ~x17 && ~x19 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x7 && ~x9 && ~x16 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x7 )
						begin
							nx_state = s10;
						end
					else if( ~x24 && x7 && x23 )
						begin
							nx_state = s20;
						end
					else if( ~x24 && x7 && ~x23 && x8 && x9 && x10 )
						begin
							nx_state = s11;
						end
					else if( ~x24 && x7 && ~x23 && x8 && x9 && ~x10 )
						begin
							nx_state = s21;
						end
					else if( ~x24 && x7 && ~x23 && x8 && ~x9 && x10 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && x7 && ~x23 && x8 && ~x9 && ~x10 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && x7 && ~x23 && ~x8 && x9 && x10 )
						begin
							nx_state = s18;
						end
					else if( ~x24 && x7 && ~x23 && ~x8 && x9 && ~x10 )
						begin
							nx_state = s24;
						end
					else if( ~x24 && x7 && ~x23 && ~x8 && ~x9 )
						begin
							nx_state = s24;
						end
					else if( ~x24 && ~x7 )
						begin
							nx_state = s10;
						end
					else nx_state = s9;
				s10 : if( x24 && x23 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && x23 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && x10 && x11 )
						begin
							nx_state = s18;
						end
					else if( x24 && ~x23 && x9 && x10 && ~x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && x14 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && x15 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && x17 && x18 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && x19 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && ~x16 )
						begin
							nx_state = s19;
						end
					else if( ~x24 && x23 )
						begin
							nx_state = s20;
						end
					else if( ~x24 && ~x23 && x8 && x9 && x10 )
						begin
							nx_state = s11;
						end
					else if( ~x24 && ~x23 && x8 && x9 && ~x10 )
						begin
							nx_state = s21;
						end
					else if( ~x24 && ~x23 && x8 && ~x9 && x10 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && ~x23 && x8 && ~x9 && ~x10 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && ~x23 && ~x8 && x9 && x10 )
						begin
							nx_state = s18;
						end
					else if( ~x24 && ~x23 && ~x8 && x9 && ~x10 )
						begin
							nx_state = s24;
						end
					else if( ~x24 && ~x23 && ~x8 && ~x9 )
						begin
							nx_state = s24;
						end
					else nx_state = s10;
				s11 : if( x23 && x11 && x12 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && x13 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( x23 && ~x11 )
						nx_state = s1;
					else if( ~x23 && x24 )
						nx_state = s1;
					else if( ~x23 && ~x24 && x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x23 && ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s11;
				s12 : if( x24 && x23 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && x23 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && x23 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x23 && x6 )
						begin
							nx_state = s9;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && x10 && x11 )
						begin
							nx_state = s18;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && x10 && ~x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && x13 && x14 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && x13 && ~x14 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && ~x13 && x15 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && x9 && ~x10 && ~x13 && ~x15 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && x17 && x18 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && x17 && ~x18 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && ~x17 && x19 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && x16 && ~x17 && ~x19 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x6 && x7 && ~x9 && ~x16 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x6 && ~x7 )
						begin
							nx_state = s10;
						end
					else if( ~x24 && x6 )
						begin
							nx_state = s9;
						end
					else if( ~x24 && ~x6 && x7 && x23 )
						begin
							nx_state = s20;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && x8 && x9 && x10 )
						begin
							nx_state = s11;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && x8 && x9 && ~x10 )
						begin
							nx_state = s21;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && x8 && ~x9 && x10 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && x8 && ~x9 && ~x10 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && ~x8 && x9 && x10 )
						begin
							nx_state = s18;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && ~x8 && x9 && ~x10 )
						begin
							nx_state = s24;
						end
					else if( ~x24 && ~x6 && x7 && ~x23 && ~x8 && ~x9 )
						begin
							nx_state = s24;
						end
					else if( ~x24 && ~x6 && ~x7 )
						begin
							nx_state = s10;
						end
					else nx_state = s12;
				s13 : if( x23 && x11 && x12 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && x13 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( x23 && ~x11 )
						nx_state = s1;
					else if( ~x23 )
						nx_state = s1;
					else nx_state = s13;
				s14 : if( x24 && x4 )
						begin
							nx_state = s3;
						end
					else if( x24 && ~x4 && x23 && x5 && x6 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && x5 && x6 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && x5 && x6 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && x5 && x6 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && x5 && ~x6 && x7 )
						begin
							nx_state = s25;
						end
					else if( x24 && ~x4 && x23 && x5 && ~x6 && ~x7 )
						begin
							nx_state = s26;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && x7 && x8 )
						begin
							nx_state = s12;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && x7 && ~x8 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && x7 && ~x8 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && x7 && ~x8 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && ~x5 && x6 && x7 && ~x8 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && ~x5 && x6 && ~x7 && x9 )
						begin
							nx_state = s12;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && ~x7 && ~x9 && x10 && x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && ~x7 && ~x9 && x10 && ~x11 && x12 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x4 && x23 && ~x5 && x6 && ~x7 && ~x9 && x10 && ~x11 && ~x12 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && ~x5 && x6 && ~x7 && ~x9 && ~x10 )
						nx_state = s1;
					else if( x24 && ~x4 && x23 && ~x5 && ~x6 && x7 )
						begin
							nx_state = s9;
						end
					else if( x24 && ~x4 && x23 && ~x5 && ~x6 && ~x7 )
						begin
							nx_state = s10;
						end
					else if( x24 && ~x4 && ~x23 && x8 )
						begin
							nx_state = s25;
						end
					else if( x24 && ~x4 && ~x23 && ~x8 )
						begin
							nx_state = s26;
						end
					else if( ~x24 && x23 && x4 && x8 && x9 && x10 )
						begin
							nx_state = s26;
						end
					else if( ~x24 && x23 && x4 && x8 && x9 && ~x10 )
						begin
							nx_state = s25;
						end
					else if( ~x24 && x23 && x4 && x8 && ~x9 && x10 )
						begin
							nx_state = s17;
						end
					else if( ~x24 && x23 && x4 && x8 && ~x9 && ~x10 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && x23 && x4 && ~x8 && x9 && x10 )
						begin
							nx_state = s11;
						end
					else if( ~x24 && x23 && x4 && ~x8 && x9 && ~x10 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && x23 && x4 && ~x8 && ~x9 && x10 )
						begin
							nx_state = s15;
						end
					else if( ~x24 && x23 && x4 && ~x8 && ~x9 && ~x10 )
						begin
							nx_state = s16;
						end
					else if( ~x24 && x23 && ~x4 )
						begin
							nx_state = s3;
						end
					else if( ~x24 && ~x23 && x4 )
						begin
							nx_state = s3;
						end
					else if( ~x24 && ~x23 && ~x4 && x8 && x9 && x10 )
						begin
							nx_state = s11;
						end
					else if( ~x24 && ~x23 && ~x4 && x8 && x9 && ~x10 )
						begin
							nx_state = s21;
						end
					else if( ~x24 && ~x23 && ~x4 && x8 && ~x9 && x10 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && ~x23 && ~x4 && x8 && ~x9 && ~x10 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && ~x23 && ~x4 && ~x8 && x9 && x10 )
						begin
							nx_state = s17;
						end
					else if( ~x24 && ~x23 && ~x4 && ~x8 && x9 && ~x10 )
						begin
							nx_state = s26;
						end
					else if( ~x24 && ~x23 && ~x4 && ~x8 && ~x9 )
						begin
							nx_state = s25;
						end
					else nx_state = s14;
				s15 : if( 1'b1 )
						begin
							nx_state = s27;
						end
					else nx_state = s15;
				s16 : if( 1'b1 )
						begin
							nx_state = s13;
						end
					else nx_state = s16;
				s17 : if( x24 && x23 )
						nx_state = s1;
					else if( x24 && ~x23 )
						begin
							nx_state = s23;
						end
					else if( ~x24 && x11 && x12 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && x12 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && x13 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && ~x12 && x13 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s17;
				s18 : if( x24 )
						begin
							nx_state = s22;
						end
					else if( ~x24 && x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s18;
				s19 : if( x23 )
						begin
							nx_state = s28;
						end
					else if( ~x23 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( ~x23 && ~x20 )
						nx_state = s1;
					else nx_state = s19;
				s20 : if( x8 )
						begin
							nx_state = s19;
						end
					else if( ~x8 && x9 && x10 )
						begin
							nx_state = s27;
						end
					else if( ~x8 && x9 && ~x10 )
						begin
							nx_state = s27;
						end
					else if( ~x8 && ~x9 && x10 )
						begin
							nx_state = s15;
						end
					else if( ~x8 && ~x9 && ~x10 )
						begin
							nx_state = s16;
						end
					else nx_state = s20;
				s21 : if( x23 && x11 && x12 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && x13 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( x23 && ~x11 )
						nx_state = s1;
					else if( ~x23 && x24 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( ~x23 && x24 && ~x20 )
						nx_state = s1;
					else if( ~x23 && ~x24 && x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x23 && ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s21;
				s22 : if( x23 && x11 && x12 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && x13 )
						begin
							nx_state = s1;
						end
					else if( x23 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( x23 && ~x11 )
						nx_state = s1;
					else if( ~x23 && x24 && x12 )
						begin
							nx_state = s21;
						end
					else if( ~x23 && x24 && ~x12 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && ~x12 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && ~x12 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( ~x23 && x24 && ~x12 && ~x20 )
						nx_state = s1;
					else if( ~x23 && ~x24 && x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x23 && ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s22;
				s23 : if( x23 )
						begin
							nx_state = s29;
						end
					else if( ~x23 && x24 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( ~x23 && x24 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( ~x23 && x24 && ~x20 )
						nx_state = s1;
					else if( ~x23 && ~x24 && x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( ~x23 && ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x23 && ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s23;
				s24 : if( x11 && x12 )
						begin
							nx_state = s13;
						end
					else if( x11 && ~x12 && x13 )
						begin
							nx_state = s13;
						end
					else if( x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x11 )
						nx_state = s1;
					else nx_state = s24;
				s25 : if( x24 && x23 )
						nx_state = s1;
					else if( x24 && ~x23 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x20 )
						nx_state = s1;
					else if( ~x24 && x11 && x12 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && x12 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && x13 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && ~x12 && x13 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s25;
				s26 : if( x24 && x23 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && x10 && x11 )
						begin
							nx_state = s18;
						end
					else if( x24 && ~x23 && x9 && x10 && ~x11 )
						begin
							nx_state = s17;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && x14 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && x13 && ~x14 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && x15 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && x9 && ~x10 && ~x13 && ~x15 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && x17 && x18 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && x17 && ~x18 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && x19 )
						begin
							nx_state = s19;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && x21 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && x22 )
						begin
							nx_state = s11;
						end
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && x20 && ~x21 && ~x22 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && x16 && ~x17 && ~x19 && ~x20 )
						nx_state = s1;
					else if( x24 && ~x23 && ~x9 && ~x16 )
						begin
							nx_state = s19;
						end
					else if( ~x24 && x11 && x12 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && x12 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && x13 && x23 )
						begin
							nx_state = s1;
						end
					else if( ~x24 && x11 && ~x12 && x13 && ~x23 )
						begin
							nx_state = s13;
						end
					else if( ~x24 && x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x24 && ~x11 )
						nx_state = s1;
					else nx_state = s26;
				s27 : if( x11 && x12 )
						begin
							nx_state = s1;
						end
					else if( x11 && ~x12 && x13 )
						begin
							nx_state = s1;
						end
					else if( x11 && ~x12 && ~x13 )
						nx_state = s1;
					else if( ~x11 )
						nx_state = s1;
					else nx_state = s27;
				s28 : if( 1'b1 )
						begin
							nx_state = s30;
						end
					else nx_state = s28;
				s29 : if( 1'b1 )
						begin
							nx_state = s21;
						end
					else nx_state = s29;
				s30 : if( 1'b1 )
						begin
							nx_state = s31;
						end
					else nx_state = s30;
				s31 : if( 1'b1 )
						begin
							nx_state = s27;
						end
					else nx_state = s31;

			default : nx_state = 0;
		endcase
	end
endmodule
