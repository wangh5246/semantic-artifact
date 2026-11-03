pragma circom 2.1.9;
include "hadwc_common_v5.circom";
template Transition() {
    signal input relation_version;
    signal input c_a_x;
    signal input c_a_y;
    signal input c_r_x;
    signal input c_r_y;
    signal input c_prev_x;
    signal input c_prev_y;
    signal input c_next_x;
    signal input c_next_y;
    signal input c_ticket_x;
    signal input c_ticket_y;
    signal input c_receipt_x;
    signal input c_receipt_y;
    signal input anchor_prev_x;
    signal input anchor_prev_y;
    signal input anchor_next_x;
    signal input anchor_next_y;
    signal input key_tag_96;
    signal input masked_native_index;
    signal input contribution_bit;
    signal input rid_128;
    signal input ctx_limb_hi;
    signal input ctx_limb_lo;
    signal input c_k_anchor_x;
    signal input c_k_anchor_y;
    // [0]=previous accepted state, [1]=next, [2]=real K-anchor. Receiver
    // authenticates their exact indices from accepted history, never pending.
    signal input cells[3][2]; signal input remainders[3][2]; signal input coords[3][2];
    signal input rho_state[3];
    signal input payload_cell[2]; signal input payload_rem[2];
    signal input mask[2]; signal input rho_mask[2];
    signal input rho_ticket; signal input rho_receipt; signal input carry;
    relation_version === 5;
    component state[3]; component com[3];
    for(var i=0;i<3;i++) {
        state[i]=State(); state[i].cell <== cells[i]; state[i].rem <== remainders[i]; state[i].xy <== coords[i];
        com[i]=Commit(40,G_STATE(),H_STATE()); com[i].message <== state[i].message; com[i].rho <== rho_state[i];
    }
    c_prev_x === com[0].point[0]; c_prev_y === com[0].point[1];
    c_next_x === com[1].point[0]; c_next_y === com[1].point[1];
    c_k_anchor_x === com[2].point[0]; c_k_anchor_y === com[2].point[1];
    anchor_prev_x === c_prev_x; anchor_prev_y === c_prev_y;
    anchor_next_x === c_next_x; anchor_next_y === c_next_y;
    component step=Distance(144000000); step.current <== coords[1]; step.reference <== coords[0];
    component anchor=Distance(10890000); anchor.current <== coords[1]; anchor.reference <== coords[2];
    for(var i=0;i<2;i++) {
        payload_cell[i] === cells[1][i]; payload_rem[i] === remainders[1][i];
    }
    contribution_bit*(contribution_bit-1) === 0;
    signal cell_index <== cells[1][1]*100+cells[1][0];
    signal native_index <== contribution_bit*(cell_index-10000)+10000;
    component mr[2]; component mc[2];
    for(var i=0;i<2;i++) { mr[i]=Bounded(128,340282366920938462946865773367900766208); mr[i].in <== mask[i]; }
    mc[0]=Commit(128,G_MASK_A(),H_MASK_A()); mc[1]=Commit(128,G_MASK_R(),H_MASK_R());
    for(var i=0;i<2;i++) {mc[i].message <== mask[i]; mc[i].rho <== rho_mask[i];}
    c_a_x === mc[0].point[0]; c_a_y === mc[0].point[1];
    c_r_x === mc[1].point[0]; c_r_y === mc[1].point[1];
    component tr=Bounded(128,340282366920938462946865773367900766208); tr.in <== masked_native_index;
    component cr=Bounded(2,2); cr.in <== carry;
    native_index+mask[0]+mask[1] === masked_native_index+carry*340282366920938462946865773367900766209;
    component rid=Num2Bits(128); rid.in <== rid_128;
    component kh=Num2Bits(96); kh.in <== key_tag_96;
    component ctx[2]; ctx[0]=Num2Bits(128); ctx[0].in <== ctx_limb_hi;
    ctx[1]=Num2Bits(128); ctx[1].in <== ctx_limb_lo;
    component ticket=Commit(224,G_TICKET(),H_TICKET());
    ticket.message <== key_tag_96*340282366920938463463374607431768211456+rid_128; ticket.rho <== rho_ticket;
    c_ticket_x === ticket.point[0]; c_ticket_y === ticket.point[1];
    component receipt=Commit(130,G_RECEIPT(),H_RECEIPT());
    receipt.message <== masked_native_index*4+contribution_bit; receipt.rho <== rho_receipt;
    c_receipt_x === receipt.point[0]; c_receipt_y === receipt.point[1];
}
component main {public [relation_version, c_a_x, c_a_y, c_r_x, c_r_y, c_prev_x, c_prev_y, c_next_x, c_next_y, c_ticket_x, c_ticket_y, c_receipt_x, c_receipt_y, anchor_prev_x, anchor_prev_y, anchor_next_x, anchor_next_y, key_tag_96, masked_native_index, contribution_bit, rid_128, ctx_limb_hi, ctx_limb_lo, c_k_anchor_x, c_k_anchor_y]} = Transition();
