module amtz ( clk,
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
	pr_state );

input clk, rst, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15,
	x16, x17, x18, x19, x20, x21, x22, x23;

parameter s1=1, s2=2, s3=3, s4=4, s5=5, s6=6, s7=7, s8=8, s9=9, s10=10,
	s11=11, s12=12, s13=13, s14=14, s15=15, s16=16, s17=17, s18=18, s19=19, s20=20,
	s21=21, s22=22, s23=23, s24=24, s25=25, s26=26, s27=27, s28=28, s29=29, s30=30,
	s31=31, s32=32, s33=33, s34=34, s35=35, s36=36, s37=37, s38=38, s39=39, s40=40,
	s41=41, s42=42, s43=43, s44=44, s45=45, s46=46, s47=47, s48=48, s49=49, s50=50,
	s51=51, s52=52, s53=53, s54=54, s55=55, s56=56, s57=57, s58=58, s59=59, s60=60,
	s61=61, s62=62, s63=63, s64=64, s65=65, s66=66, s67=67, s68=68, s69=69, s70=70,
	s71=71, s72=72, s73=73, s74=74, s75=75, s76=76, s77=77, s78=78, s79=79, s80=80,
	s81=81, s82=82, s83=83, s84=84, s85=85;

output reg [6:0] pr_state;
reg [6:0] nx_state;
always@ ( posedge rst or negedge clk )
begin
	if ( rst == 1'b1 )
		pr_state <= s1;
	else
		pr_state <= nx_state;
end

always@ ( pr_state or x1 or x2 or x3 or x4 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or x13 or x14 or x15 or 
	x16 or x17 or x18 or x19 or x20 or x21 or x22 or x23)
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
							nx_state = s8;
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
							nx_state = s16;
						end
					else nx_state = s14;
				s15 : if( x17 )
						begin
							nx_state = s17;
						end
					else if( ~x17 )
						begin
							nx_state = s13;
						end
					else nx_state = s15;
				s16 : if( 1'b1 )
						begin
							nx_state = s18;
						end
					else nx_state = s16;
				s17 : if( x18 && x22 && x23 && x3 && x4 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && x3 && x4 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && x3 && x4 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x18 && x22 && x23 && x3 && x4 && ~x21 )
						nx_state = s1;
					else if( x18 && x22 && x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && ~x3 && x4 && x5 && x15 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && x21 && ~x16 )
						nx_state = s1;
					else if( x18 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && ~x21 )
						nx_state = s1;
					else if( x18 && x22 && x23 && ~x3 && x4 && ~x5 && x16 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && x21 && x15 )
						begin
							nx_state = s1;
						end
					else if( x18 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && x21 && ~x15 )
						nx_state = s1;
					else if( x18 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && ~x21 )
						nx_state = s1;
					else if( x18 && x22 && x23 && ~x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && x23 && ~x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && x9 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && x3 && x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && x3 && x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && ~x3 && x8 )
						begin
							nx_state = s19;
						end
					else if( x18 && x22 && ~x23 && ~x9 && ~x3 && ~x8 )
						begin
							nx_state = s20;
						end
					else if( x18 && ~x22 && x23 && x9 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && x23 && ~x9 && x10 && x8 )
						begin
							nx_state = s21;
						end
					else if( x18 && ~x22 && x23 && ~x9 && x10 && ~x8 )
						begin
							nx_state = s20;
						end
					else if( x18 && ~x22 && x23 && ~x9 && ~x10 )
						begin
							nx_state = s20;
						end
					else if( x18 && ~x22 && ~x23 && x3 && x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && ~x23 && x3 && x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && ~x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && ~x23 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && ~x23 && ~x3 && x8 )
						begin
							nx_state = s19;
						end
					else if( x18 && ~x22 && ~x23 && ~x3 && ~x8 )
						begin
							nx_state = s20;
						end
					else if( ~x18 )
						begin
							nx_state = s22;
						end
					else nx_state = s17;
				s18 : if( x17 )
						begin
							nx_state = s23;
						end
					else if( ~x17 )
						begin
							nx_state = s16;
						end
					else nx_state = s18;
				s19 : if( x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x21 )
						nx_state = s1;
					else nx_state = s19;
				s20 : if( x7 )
						begin
							nx_state = s24;
						end
					else if( ~x7 && x19 && x23 && x3 && x4 && x5 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && x3 && x4 && x5 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && x3 && x4 && x5 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && x3 && x4 && x5 && ~x21 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && x3 && x4 && ~x5 )
						begin
							nx_state = s25;
						end
					else if( ~x7 && x19 && x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s26;
						end
					else if( ~x7 && x19 && x23 && x3 && ~x4 && ~x5 && x13 )
						begin
							nx_state = s19;
						end
					else if( ~x7 && x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && ~x21 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && ~x3 && x4 && x5 && x12 )
						begin
							nx_state = s19;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && ~x3 && x4 && x5 && ~x12 && ~x21 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && ~x3 && x4 && ~x5 && x11 )
						begin
							nx_state = s19;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x7 && x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && ~x21 )
						nx_state = s1;
					else if( ~x7 && x19 && x23 && ~x3 && ~x4 )
						begin
							nx_state = s19;
						end
					else if( ~x7 && x19 && ~x23 && x22 && x4 && x5 )
						begin
							nx_state = s27;
						end
					else if( ~x7 && x19 && ~x23 && x22 && x4 && ~x5 )
						begin
							nx_state = s28;
						end
					else if( ~x7 && x19 && ~x23 && x22 && ~x4 )
						begin
							nx_state = s29;
						end
					else if( ~x7 && x19 && ~x23 && ~x22 )
						begin
							nx_state = s25;
						end
					else if( ~x7 && ~x19 )
						begin
							nx_state = s30;
						end
					else nx_state = s20;
				s21 : if( 1'b1 )
						begin
							nx_state = s31;
						end
					else nx_state = s21;
				s22 : if( x6 )
						begin
							nx_state = s3;
						end
					else if( ~x6 && x22 && x23 && x3 && x4 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && x3 && x4 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && x3 && x4 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && x3 && x4 && ~x21 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && ~x3 && x4 && x5 && x15 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && x21 && ~x16 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && ~x3 && x4 && x5 && ~x15 && ~x21 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && ~x3 && x4 && ~x5 && x16 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && x21 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x6 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && x21 && ~x15 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && ~x3 && x4 && ~x5 && ~x16 && ~x21 )
						nx_state = s1;
					else if( ~x6 && x22 && x23 && ~x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && x23 && ~x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && x9 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && x3 && x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && x3 && x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && ~x3 && x7 )
						begin
							nx_state = s30;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && ~x3 && ~x7 && x4 && x5 )
						begin
							nx_state = s32;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && ~x3 && ~x7 && x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && x22 && ~x23 && ~x9 && ~x3 && ~x7 && ~x4 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && x23 && x9 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && x23 && ~x9 )
						begin
							nx_state = s30;
						end
					else if( ~x6 && ~x22 && ~x23 && x3 && x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && ~x23 && x3 && x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && ~x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && ~x23 && x3 && ~x4 && ~x5 )
						begin
							nx_state = s19;
						end
					else if( ~x6 && ~x22 && ~x23 && ~x3 && x7 )
						begin
							nx_state = s30;
						end
					else if( ~x6 && ~x22 && ~x23 && ~x3 && ~x7 )
						begin
							nx_state = s19;
						end
					else nx_state = s22;
				s23 : if( 1'b1 )
						begin
							nx_state = s33;
						end
					else nx_state = s23;
				s24 : if( 1'b1 )
						begin
							nx_state = s34;
						end
					else nx_state = s24;
				s25 : if( 1'b1 )
						begin
							nx_state = s35;
						end
					else nx_state = s25;
				s26 : if( 1'b1 )
						begin
							nx_state = s36;
						end
					else nx_state = s26;
				s27 : if( 1'b1 )
						begin
							nx_state = s37;
						end
					else nx_state = s27;
				s28 : if( 1'b1 )
						begin
							nx_state = s38;
						end
					else nx_state = s28;
				s29 : if( 1'b1 )
						begin
							nx_state = s39;
						end
					else nx_state = s29;
				s30 : if( x23 && x3 && x4 && x5 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x23 && x3 && x4 && x5 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x23 && x3 && x4 && x5 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x23 && x3 && x4 && x5 && ~x21 )
						nx_state = s1;
					else if( x23 && x3 && x4 && ~x5 )
						begin
							nx_state = s25;
						end
					else if( x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s26;
						end
					else if( x23 && x3 && ~x4 && ~x5 && x13 )
						begin
							nx_state = s19;
						end
					else if( x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x23 && x3 && ~x4 && ~x5 && ~x13 && ~x21 )
						nx_state = s1;
					else if( x23 && ~x3 && x4 && x5 && x12 )
						begin
							nx_state = s19;
						end
					else if( x23 && ~x3 && x4 && x5 && ~x12 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x23 && ~x3 && x4 && x5 && ~x12 && ~x21 )
						nx_state = s1;
					else if( x23 && ~x3 && x4 && ~x5 && x11 )
						begin
							nx_state = s19;
						end
					else if( x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x23 && ~x3 && x4 && ~x5 && ~x11 && ~x21 )
						nx_state = s1;
					else if( x23 && ~x3 && ~x4 )
						begin
							nx_state = s19;
						end
					else if( ~x23 && x22 && x4 && x5 )
						begin
							nx_state = s27;
						end
					else if( ~x23 && x22 && x4 && ~x5 )
						begin
							nx_state = s28;
						end
					else if( ~x23 && x22 && ~x4 )
						begin
							nx_state = s29;
						end
					else if( ~x23 && ~x22 )
						begin
							nx_state = s25;
						end
					else nx_state = s30;
				s31 : if( x14 )
						begin
							nx_state = s19;
						end
					else if( ~x14 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( ~x14 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( ~x14 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( ~x14 && ~x21 )
						nx_state = s1;
					else nx_state = s31;
				s32 : if( 1'b1 )
						begin
							nx_state = s40;
						end
					else nx_state = s32;
				s33 : if( 1'b1 )
						begin
							nx_state = s41;
						end
					else nx_state = s33;
				s34 : if( 1'b1 )
						begin
							nx_state = s42;
						end
					else nx_state = s34;
				s35 : if( 1'b1 )
						begin
							nx_state = s43;
						end
					else nx_state = s35;
				s36 : if( 1'b1 )
						begin
							nx_state = s44;
						end
					else nx_state = s36;
				s37 : if( 1'b1 )
						begin
							nx_state = s45;
						end
					else nx_state = s37;
				s38 : if( 1'b1 )
						begin
							nx_state = s46;
						end
					else nx_state = s38;
				s39 : if( 1'b1 )
						begin
							nx_state = s47;
						end
					else nx_state = s39;
				s40 : if( 1'b1 )
						begin
							nx_state = s19;
						end
					else nx_state = s40;
				s41 : if( 1'b1 )
						begin
							nx_state = s1;
						end
					else nx_state = s41;
				s42 : if( 1'b1 )
						begin
							nx_state = s48;
						end
					else nx_state = s42;
				s43 : if( 1'b1 )
						begin
							nx_state = s49;
						end
					else nx_state = s43;
				s44 : if( 1'b1 )
						begin
							nx_state = s50;
						end
					else nx_state = s44;
				s45 : if( 1'b1 )
						begin
							nx_state = s51;
						end
					else nx_state = s45;
				s46 : if( 1'b1 )
						begin
							nx_state = s52;
						end
					else nx_state = s46;
				s47 : if( 1'b1 )
						begin
							nx_state = s53;
						end
					else nx_state = s47;
				s48 : if( x17 )
						begin
							nx_state = s54;
						end
					else if( ~x17 )
						begin
							nx_state = s42;
						end
					else nx_state = s48;
				s49 : if( 1'b1 )
						begin
							nx_state = s55;
						end
					else nx_state = s49;
				s50 : if( x17 )
						begin
							nx_state = s56;
						end
					else if( ~x17 )
						begin
							nx_state = s44;
						end
					else nx_state = s50;
				s51 : if( 1'b1 )
						begin
							nx_state = s57;
						end
					else nx_state = s51;
				s52 : if( x17 )
						begin
							nx_state = s58;
						end
					else if( ~x17 )
						begin
							nx_state = s46;
						end
					else nx_state = s52;
				s53 : if( 1'b1 )
						begin
							nx_state = s59;
						end
					else nx_state = s53;
				s54 : if( 1'b1 )
						begin
							nx_state = s60;
						end
					else nx_state = s54;
				s55 : if( 1'b1 )
						begin
							nx_state = s61;
						end
					else nx_state = s55;
				s56 : if( 1'b1 )
						begin
							nx_state = s62;
						end
					else nx_state = s56;
				s57 : if( 1'b1 )
						begin
							nx_state = s63;
						end
					else nx_state = s57;
				s58 : if( 1'b1 )
						begin
							nx_state = s64;
						end
					else nx_state = s58;
				s59 : if( x17 )
						begin
							nx_state = s65;
						end
					else if( ~x17 )
						begin
							nx_state = s53;
						end
					else nx_state = s59;
				s60 : if( 1'b1 )
						begin
							nx_state = s66;
						end
					else nx_state = s60;
				s61 : if( x17 )
						begin
							nx_state = s67;
						end
					else if( ~x17 )
						begin
							nx_state = s55;
						end
					else nx_state = s61;
				s62 : if( 1'b1 )
						begin
							nx_state = s68;
						end
					else nx_state = s62;
				s63 : if( 1'b1 )
						begin
							nx_state = s69;
						end
					else nx_state = s63;
				s64 : if( 1'b1 )
						begin
							nx_state = s70;
						end
					else nx_state = s64;
				s65 : if( 1'b1 )
						begin
							nx_state = s71;
						end
					else nx_state = s65;
				s66 : if( x19 && x23 && x3 && x4 && x5 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && x3 && x4 && x5 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && x3 && x4 && x5 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x19 && x23 && x3 && x4 && x5 && ~x21 )
						nx_state = s1;
					else if( x19 && x23 && x3 && x4 && ~x5 )
						begin
							nx_state = s25;
						end
					else if( x19 && x23 && x3 && ~x4 && x5 )
						begin
							nx_state = s26;
						end
					else if( x19 && x23 && x3 && ~x4 && ~x5 && x13 )
						begin
							nx_state = s19;
						end
					else if( x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x19 && x23 && x3 && ~x4 && ~x5 && ~x13 && ~x21 )
						nx_state = s1;
					else if( x19 && x23 && ~x3 && x4 && x5 && x12 )
						begin
							nx_state = s19;
						end
					else if( x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && ~x3 && x4 && x5 && ~x12 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x19 && x23 && ~x3 && x4 && x5 && ~x12 && ~x21 )
						nx_state = s1;
					else if( x19 && x23 && ~x3 && x4 && ~x5 && x11 )
						begin
							nx_state = s19;
						end
					else if( x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x19 && x23 && ~x3 && x4 && ~x5 && ~x11 && ~x21 )
						nx_state = s1;
					else if( x19 && x23 && ~x3 && ~x4 )
						begin
							nx_state = s19;
						end
					else if( x19 && ~x23 && x22 && x4 && x5 )
						begin
							nx_state = s27;
						end
					else if( x19 && ~x23 && x22 && x4 && ~x5 )
						begin
							nx_state = s28;
						end
					else if( x19 && ~x23 && x22 && ~x4 )
						begin
							nx_state = s29;
						end
					else if( x19 && ~x23 && ~x22 )
						begin
							nx_state = s25;
						end
					else if( ~x19 )
						begin
							nx_state = s30;
						end
					else nx_state = s66;
				s67 : if( x20 && x23 )
						begin
							nx_state = s31;
						end
					else if( x20 && ~x23 )
						begin
							nx_state = s19;
						end
					else if( ~x20 )
						begin
							nx_state = s35;
						end
					else nx_state = s67;
				s68 : if( 1'b1 )
						begin
							nx_state = s72;
						end
					else nx_state = s68;
				s69 : if( 1'b1 )
						begin
							nx_state = s73;
						end
					else nx_state = s69;
				s70 : if( x20 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x20 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x20 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x20 && ~x21 )
						nx_state = s1;
					else if( ~x20 )
						begin
							nx_state = s38;
						end
					else nx_state = s70;
				s71 : if( x20 )
						begin
							nx_state = s19;
						end
					else if( ~x20 )
						begin
							nx_state = s39;
						end
					else nx_state = s71;
				s72 : if( 1'b1 )
						begin
							nx_state = s74;
						end
					else nx_state = s72;
				s73 : if( x17 )
						begin
							nx_state = s75;
						end
					else if( ~x17 )
						begin
							nx_state = s69;
						end
					else nx_state = s73;
				s74 : if( x17 )
						begin
							nx_state = s76;
						end
					else if( ~x17 )
						begin
							nx_state = s72;
						end
					else nx_state = s74;
				s75 : if( x20 )
						begin
							nx_state = s77;
						end
					else if( ~x20 )
						begin
							nx_state = s51;
						end
					else nx_state = s75;
				s76 : if( 1'b1 )
						begin
							nx_state = s78;
						end
					else nx_state = s76;
				s77 : if( 1'b1 )
						begin
							nx_state = s79;
						end
					else nx_state = s77;
				s78 : if( 1'b1 )
						begin
							nx_state = s19;
						end
					else nx_state = s78;
				s79 : if( 1'b1 )
						begin
							nx_state = s80;
						end
					else nx_state = s79;
				s80 : if( 1'b1 )
						begin
							nx_state = s81;
						end
					else nx_state = s80;
				s81 : if( 1'b1 )
						begin
							nx_state = s82;
						end
					else nx_state = s81;
				s82 : if( x17 )
						begin
							nx_state = s83;
						end
					else if( ~x17 )
						begin
							nx_state = s81;
						end
					else nx_state = s82;
				s83 : if( 1'b1 )
						begin
							nx_state = s84;
						end
					else nx_state = s83;
				s84 : if( 1'b1 )
						begin
							nx_state = s85;
						end
					else nx_state = s84;
				s85 : if( x20 && x21 && x16 )
						begin
							nx_state = s1;
						end
					else if( x20 && x21 && ~x16 && x15 )
						begin
							nx_state = s1;
						end
					else if( x20 && x21 && ~x16 && ~x15 )
						nx_state = s1;
					else if( x20 && ~x21 )
						nx_state = s1;
					else if( ~x20 )
						begin
							nx_state = s80;
						end
					else nx_state = s85;

			default : nx_state = 0;
		endcase
	end
endmodule
