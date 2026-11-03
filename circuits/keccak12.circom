pragma circom 2.1.9;
template Xor() {signal input a;signal input b;signal output out;out <== a+b-2*a*b;}
template Round(RC) {
 signal input in[25][64]; signal output out[25][64];
 component c[5][64][4];component d[5][64];component t[25][64];
 signal b[25][64];signal term[25][64];component z[25][64];
 var rotation[5][5]=[[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]];
 for(var x=0;x<5;x++) for(var bit=0;bit<64;bit++) for(var k=0;k<4;k++) {
  c[x][bit][k]=Xor();
  if(k==0) c[x][bit][k].a <== in[x][bit]; else c[x][bit][k].a <== c[x][bit][k-1].out;
  c[x][bit][k].b <== in[x+5*(k+1)][bit];
 }
 for(var x=0;x<5;x++) for(var bit=0;bit<64;bit++) {
  d[x][bit]=Xor();d[x][bit].a <== c[(x+4)%5][bit][3].out;
  d[x][bit].b <== c[(x+1)%5][(bit+63)%64][3].out;
 }
 for(var y=0;y<5;y++) for(var x=0;x<5;x++) for(var bit=0;bit<64;bit++) {
  var lane=x+5*y;t[lane][bit]=Xor();t[lane][bit].a <== in[lane][bit];t[lane][bit].b <== d[x][bit].out;
  b[y+5*((2*x+3*y)%5)][(bit+rotation[x][y])%64] <== t[lane][bit].out;
 }
 for(var y=0;y<5;y++) for(var x=0;x<5;x++) for(var bit=0;bit<64;bit++) {
  var lane=x+5*y;term[lane][bit] <== (1-b[(x+1)%5+5*y][bit])*b[(x+2)%5+5*y][bit];
  z[lane][bit]=Xor();z[lane][bit].a <== b[lane][bit];z[lane][bit].b <== term[lane][bit];
  if(lane==0 && ((RC >> bit)&1)==1) out[lane][bit] <== 1-z[lane][bit].out;
  else out[lane][bit] <== z[lane][bit].out;
 }
}
template K() {
 signal input in[1600];signal output out[1600];component rounds[12];var rc[12]=[2147516555, 9223372036854775947, 9223372036854808713, 9223372036854808579, 9223372036854808578, 9223372036854775936, 32778, 9223372039002259466, 9223372039002292353, 9223372036854808704, 2147483649, 9223372039002292232];
 for(var i=0;i<1600;i++) in[i]*(in[i]-1)===0;
 for(var r=0;r<12;r++) {
  rounds[r]=Round(rc[r]);
  for(var lane=0;lane<25;lane++) for(var bit=0;bit<64;bit++) {
   if(r==0) rounds[r].in[lane][bit] <== in[lane*64+bit];
   else rounds[r].in[lane][bit] <== rounds[r-1].out[lane][bit];
  }
 }
 for(var i=0;i<1600;i++) out[i] <== rounds[11].out[i\64][i%64];
}
component main=K();
