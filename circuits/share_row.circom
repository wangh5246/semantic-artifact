pragma circom 2.1.9;
include "circomlib/circuits/bitify.circom";
include "circomlib/circuits/comparators.circom";
template ShareRow(){
 signal input helper_bits[128];signal input leader;signal input primary;signal input position;signal input carry;
 signal output selected;
 signal helper;
 var weighted=0;
 for(var i=0;i<128;i++){weighted += helper_bits[i]*(2**i);}
 helper <== weighted;
 component canon_h=LessThan(128);canon_h.in[0] <== helper;canon_h.in[1] <== 340282366920938462946865773367900766209;canon_h.out === 1;
 component leader_bits=Num2Bits(128);leader_bits.in <== leader;
 component canon_l=LessThan(128);canon_l.in[0] <== leader;canon_l.in[1] <== 340282366920938462946865773367900766209;canon_l.out === 1;
 component eq=IsEqual();eq.in[0] <== primary;eq.in[1] <== position;selected <== eq.out;
 carry*(carry-1)===0;
 helper+leader === selected+carry*340282366920938462946865773367900766209;
}
component main=ShareRow();
