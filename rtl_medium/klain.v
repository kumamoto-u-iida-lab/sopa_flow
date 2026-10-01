module klain ( clk,
	rst,
	x1,
	x2,
	x3,
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
	x20,
	x21,
	x22,
	x23,
	x24,
	x25,
	x26,
	x27,
	pr_state );

input clk, rst, x1, x2, x3, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15,
	x16, x17, x18, x20, x21, x22, x23, x24, x25, x26, x27;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23, s24=24, s25=25, s26=26, s27=27, s28=28, s29=29, s30=30,
	s31=31, s32=32, s33=33, s34=34, s35=35, s36=36, s37=37, s38=38, s39=39, s40=40,
	s41=41, s42=42, s43=43, s44=44, s45=45, s46=46, s47=47, s48=48, s49=49, s50=50,
	s51=51, s52=52, s53=53, s54=54;

output reg [5:0] pr_state;
reg [5:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or x13 or x14 or x15 or 
	x16 or x17 or x18 or x20 or x21 or x22 or x23 or x24 or x25 or x26 or x27)
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
				s7 : if( 1'b1 )
						begin
							nx_state = s9;
						end
					else nx_state = s7;
				s8 : if( 1'b1 )
						begin
							nx_state = s10;
						end
					else nx_state = s8;
				s9 : if( 1'b1 )
						begin
							nx_state = s11;
						end
					else nx_state = s9;
				s10 : if( x17 )
						begin
							nx_state = s12;
						end
					else if( ~x17 )
						begin
							nx_state = s10;
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
				s13 : if( 1'b1 )
						begin
							nx_state = s15;
						end
					else nx_state = s13;
				s14 : if( 1'b1 )
						begin
							nx_state = s1;
						end
					else nx_state = s14;
				s15 : if( x17 )
						begin
							nx_state = s16;
						end
					else if( ~x17 )
						begin
							nx_state = s15;
						end
					else nx_state = s15;
				s16 : if( x18 && x26 && x14 && x27 && x6 && x3 )
						begin
							nx_state = s20;
						end
					else if( x18 && x26 && x14 && x27 && x6 && ~x3 )
						begin
							nx_state = s21;
						end
					else if( x18 && x26 && x14 && x27 && ~x6 && x5 )
						begin
							nx_state = s17;
						end
					else if( x18 && x26 && x14 && x27 && ~x6 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( x18 && x26 && x14 && ~x27 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x26 && x14 && ~x27 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( x18 && x26 && ~x14 && x3 )
						begin
							nx_state = s20;
						end
					else if( x18 && x26 && ~x14 && ~x3 )
						begin
							nx_state = s21;
						end
					else if( x18 && ~x26 && x27 && x14 && x5 )
						begin
							nx_state = s22;
						end
					else if( x18 && ~x26 && x27 && x14 && ~x5 )
						begin
							nx_state = s17;
						end
					else if( x18 && ~x26 && x27 && ~x14 )
						begin
							nx_state = s20;
						end
					else if( x18 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && x6 && x7 && x22 && ~x23 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && x6 && x7 && ~x22 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x26 && ~x27 && x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && x15 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && ~x23 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && ~x22 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && x16 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && ~x23 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && ~x22 )
						nx_state = s1;
					else if( x18 && ~x26 && ~x27 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x26 && ~x27 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( ~x18 )
						begin
							nx_state = s23;
						end
					else nx_state = s16;
				s17 : if( x3 && x21 && x26 && x27 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && x26 && x27 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && x26 && x27 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x3 && x21 && x26 && x27 && x22 && ~x23 )
						nx_state = s1;
					else if( x3 && x21 && x26 && x27 && ~x22 )
						nx_state = s1;
					else if( x3 && x21 && x26 && ~x27 )
						begin
							nx_state = s6;
						end
					else if( x3 && x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && x6 && x7 && x8 && x22 && ~x23 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && x6 && x7 && x8 && ~x22 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && x6 && x7 && ~x8 )
						begin
							nx_state = s8;
						end
					else if( x3 && x21 && ~x26 && x6 && ~x7 && x8 )
						begin
							nx_state = s24;
						end
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && x11 )
						begin
							nx_state = s19;
						end
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && ~x23 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && ~x22 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && x9 )
						begin
							nx_state = s19;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && ~x23 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && ~x22 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && x10 )
						begin
							nx_state = s19;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && ~x23 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && ~x22 )
						nx_state = s1;
					else if( x3 && x21 && ~x26 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x3 && x21 && ~x26 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s25;
						end
					else if( x3 && ~x21 )
						begin
							nx_state = s26;
						end
					else if( ~x3 )
						begin
							nx_state = s27;
						end
					else nx_state = s17;
				s18 : if( x26 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x26 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x26 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x26 && x22 && ~x23 )
						nx_state = s1;
					else if( x26 && ~x22 )
						nx_state = s1;
					else if( ~x26 && x12 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x12 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x12 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && x12 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && x12 && ~x22 )
						nx_state = s1;
					else if( ~x26 && ~x12 )
						begin
							nx_state = s19;
						end
					else nx_state = s18;
				s19 : if( x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x22 && ~x23 )
						nx_state = s1;
					else if( ~x22 )
						nx_state = s1;
					else nx_state = s19;
				s20 : if( x26 && x27 )
						begin
							nx_state = s28;
						end
					else if( x26 && ~x27 )
						begin
							nx_state = s6;
						end
					else if( ~x26 && x12 )
						begin
							nx_state = s19;
						end
					else if( ~x26 && ~x12 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x12 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x12 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && ~x12 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && ~x12 && ~x22 )
						nx_state = s1;
					else nx_state = s20;
				s21 : if( x27 && x6 && x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && x6 && x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && ~x6 && x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && ~x6 && x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x27 && ~x6 && ~x7 )
						begin
							nx_state = s19;
						end
					else if( ~x27 && x7 && x6 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x27 && x7 && x6 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( ~x27 && x7 && ~x6 && x13 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x27 && x7 && ~x6 && x13 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x27 && x7 && ~x6 && x13 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && x13 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && x13 && ~x22 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && ~x13 && x3 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x27 && x7 && ~x6 && ~x13 && x3 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x27 && x7 && ~x6 && ~x13 && x3 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && ~x13 && x3 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && ~x13 && x3 && ~x22 )
						nx_state = s1;
					else if( ~x27 && x7 && ~x6 && ~x13 && ~x3 )
						begin
							nx_state = s29;
						end
					else if( ~x27 && ~x7 && x6 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x27 && ~x7 && x6 && ~x8 )
						begin
							nx_state = s30;
						end
					else if( ~x27 && ~x7 && ~x6 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x27 && ~x7 && ~x6 && ~x8 )
						begin
							nx_state = s19;
						end
					else nx_state = s21;
				s22 : if( 1'b1 )
						begin
							nx_state = s18;
						end
					else nx_state = s22;
				s23 : if( x13 )
						begin
							nx_state = s5;
						end
					else if( ~x13 && x26 && x14 && x27 && x6 && x3 )
						begin
							nx_state = s20;
						end
					else if( ~x13 && x26 && x14 && x27 && x6 && ~x3 )
						begin
							nx_state = s21;
						end
					else if( ~x13 && x26 && x14 && x27 && ~x6 && x5 )
						begin
							nx_state = s17;
						end
					else if( ~x13 && x26 && x14 && x27 && ~x6 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x13 && x26 && x14 && ~x27 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && x26 && x14 && ~x27 && ~x5 )
						begin
							nx_state = s18;
						end
					else if( ~x13 && x26 && ~x14 && x3 )
						begin
							nx_state = s20;
						end
					else if( ~x13 && x26 && ~x14 && ~x3 )
						begin
							nx_state = s21;
						end
					else if( ~x13 && ~x26 && x27 && x14 && x5 )
						begin
							nx_state = s22;
						end
					else if( ~x13 && ~x26 && x27 && x14 && ~x5 )
						begin
							nx_state = s17;
						end
					else if( ~x13 && ~x26 && x27 && ~x14 )
						begin
							nx_state = s20;
						end
					else if( ~x13 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && x6 && x7 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && x6 && x7 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && x6 && x7 && ~x22 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && ~x26 && ~x27 && x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && x15 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && x8 && ~x15 && ~x22 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && x16 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && x7 && ~x8 && ~x16 && ~x22 )
						nx_state = s1;
					else if( ~x13 && ~x26 && ~x27 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x13 && ~x26 && ~x27 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else nx_state = s23;
				s24 : if( 1'b1 )
						begin
							nx_state = s31;
						end
					else nx_state = s24;
				s25 : if( 1'b1 )
						begin
							nx_state = s19;
						end
					else nx_state = s25;
				s26 : if( x26 && x27 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x26 && x27 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x26 && x27 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x26 && x27 && x22 && ~x23 )
						nx_state = s1;
					else if( x26 && x27 && ~x22 )
						nx_state = s1;
					else if( x26 && ~x27 )
						begin
							nx_state = s6;
						end
					else if( ~x26 && x6 && x7 && x8 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && x6 && x7 && x8 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && x6 && x7 && x8 && ~x22 )
						nx_state = s1;
					else if( ~x26 && x6 && x7 && ~x8 )
						begin
							nx_state = s8;
						end
					else if( ~x26 && x6 && ~x7 && x8 )
						begin
							nx_state = s24;
						end
					else if( ~x26 && x6 && ~x7 && ~x8 && x11 )
						begin
							nx_state = s19;
						end
					else if( ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && x6 && ~x7 && ~x8 && ~x11 && ~x22 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && x8 && x9 )
						begin
							nx_state = s19;
						end
					else if( ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && x8 && ~x9 && ~x22 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && ~x8 && x10 )
						begin
							nx_state = s19;
						end
					else if( ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x26 && ~x6 && x7 && ~x8 && ~x10 && ~x22 )
						nx_state = s1;
					else if( ~x26 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( ~x26 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s25;
						end
					else nx_state = s26;
				s27 : if( 1'b1 )
						begin
							nx_state = s32;
						end
					else nx_state = s27;
				s28 : if( 1'b1 )
						begin
							nx_state = s33;
						end
					else nx_state = s28;
				s29 : if( x8 )
						begin
							nx_state = s19;
						end
					else if( ~x8 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( ~x8 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( ~x8 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( ~x8 && x22 && ~x23 )
						nx_state = s1;
					else if( ~x8 && ~x22 )
						nx_state = s1;
					else nx_state = s29;
				s30 : if( 1'b1 )
						begin
							nx_state = s34;
						end
					else nx_state = s30;
				s31 : if( 1'b1 )
						begin
							nx_state = s35;
						end
					else nx_state = s31;
				s32 : if( 1'b1 )
						begin
							nx_state = s36;
						end
					else nx_state = s32;
				s33 : if( 1'b1 )
						begin
							nx_state = s37;
						end
					else nx_state = s33;
				s34 : if( 1'b1 )
						begin
							nx_state = s38;
						end
					else nx_state = s34;
				s35 : if( x17 )
						begin
							nx_state = s39;
						end
					else if( ~x17 )
						begin
							nx_state = s35;
						end
					else nx_state = s35;
				s36 : if( 1'b1 )
						begin
							nx_state = s40;
						end
					else nx_state = s36;
				s37 : if( 1'b1 )
						begin
							nx_state = s41;
						end
					else nx_state = s37;
				s38 : if( x17 )
						begin
							nx_state = s42;
						end
					else if( ~x17 )
						begin
							nx_state = s38;
						end
					else nx_state = s38;
				s39 : if( 1'b1 )
						begin
							nx_state = s25;
						end
					else nx_state = s39;
				s40 : if( x17 )
						begin
							nx_state = s43;
						end
					else if( ~x17 )
						begin
							nx_state = s40;
						end
					else nx_state = s40;
				s41 : if( x17 )
						begin
							nx_state = s44;
						end
					else if( ~x17 )
						begin
							nx_state = s41;
						end
					else nx_state = s41;
				s42 : if( 1'b1 )
						begin
							nx_state = s45;
						end
					else nx_state = s42;
				s43 : if( x20 )
						begin
							nx_state = s46;
						end
					else if( ~x20 )
						begin
							nx_state = s36;
						end
					else nx_state = s43;
				s44 : if( 1'b1 )
						begin
							nx_state = s47;
						end
					else nx_state = s44;
				s45 : if( x20 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x20 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x20 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x20 && x22 && ~x23 )
						nx_state = s1;
					else if( x20 && ~x22 )
						nx_state = s1;
					else if( ~x20 )
						begin
							nx_state = s34;
						end
					else nx_state = s45;
				s46 : if( x21 && x26 && x27 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x21 && x26 && x27 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x21 && x26 && x27 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x21 && x26 && x27 && x22 && ~x23 )
						nx_state = s1;
					else if( x21 && x26 && x27 && ~x22 )
						nx_state = s1;
					else if( x21 && x26 && ~x27 )
						begin
							nx_state = s6;
						end
					else if( x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && x6 && x7 && x8 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x21 && ~x26 && x6 && x7 && x8 && x22 && ~x23 )
						nx_state = s1;
					else if( x21 && ~x26 && x6 && x7 && x8 && ~x22 )
						nx_state = s1;
					else if( x21 && ~x26 && x6 && x7 && ~x8 )
						begin
							nx_state = s8;
						end
					else if( x21 && ~x26 && x6 && ~x7 && x8 )
						begin
							nx_state = s24;
						end
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && x11 )
						begin
							nx_state = s19;
						end
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && x22 && ~x23 )
						nx_state = s1;
					else if( x21 && ~x26 && x6 && ~x7 && ~x8 && ~x11 && ~x22 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && x8 && x9 )
						begin
							nx_state = s19;
						end
					else if( x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && x22 && ~x23 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && x8 && ~x9 && ~x22 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && x10 )
						begin
							nx_state = s19;
						end
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && x22 && ~x23 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && x7 && ~x8 && ~x10 && ~x22 )
						nx_state = s1;
					else if( x21 && ~x26 && ~x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x21 && ~x26 && ~x6 && ~x7 && ~x8 )
						begin
							nx_state = s25;
						end
					else if( ~x21 )
						begin
							nx_state = s26;
						end
					else nx_state = s46;
				s47 : if( x20 && x26 && x27 && x6 && x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && x6 && x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && x6 && ~x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && x6 && ~x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && ~x6 && x7 && x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && ~x6 && x7 && ~x8 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && x27 && ~x6 && ~x7 )
						begin
							nx_state = s19;
						end
					else if( x20 && x26 && ~x27 )
						begin
							nx_state = s21;
						end
					else if( x20 && ~x26 )
						begin
							nx_state = s48;
						end
					else if( ~x20 )
						begin
							nx_state = s37;
						end
					else nx_state = s47;
				s48 : if( 1'b1 )
						begin
							nx_state = s49;
						end
					else nx_state = s48;
				s49 : if( 1'b1 )
						begin
							nx_state = s50;
						end
					else nx_state = s49;
				s50 : if( 1'b1 )
						begin
							nx_state = s51;
						end
					else nx_state = s50;
				s51 : if( 1'b1 )
						begin
							nx_state = s52;
						end
					else nx_state = s51;
				s52 : if( x17 )
						begin
							nx_state = s53;
						end
					else if( ~x17 )
						begin
							nx_state = s52;
						end
					else nx_state = s52;
				s53 : if( 1'b1 )
						begin
							nx_state = s54;
						end
					else nx_state = s53;
				s54 : if( x20 && x12 )
						begin
							nx_state = s19;
						end
					else if( x20 && ~x12 && x22 && x23 && x24 )
						begin
							nx_state = s1;
						end
					else if( x20 && ~x12 && x22 && x23 && ~x24 && x25 )
						begin
							nx_state = s1;
						end
					else if( x20 && ~x12 && x22 && x23 && ~x24 && ~x25 )
						nx_state = s1;
					else if( x20 && ~x12 && x22 && ~x23 )
						nx_state = s1;
					else if( x20 && ~x12 && ~x22 )
						nx_state = s1;
					else if( ~x20 )
						begin
							nx_state = s51;
						end
					else nx_state = s54;

			default : nx_state = 0;
		endcase
	end
endmodule
