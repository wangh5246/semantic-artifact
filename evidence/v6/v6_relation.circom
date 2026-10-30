pragma circom 2.1.9;
include "../v6-inputs/hadwc_common_v5.circom";
include "circomlib/circuits/poseidon.circom";

// Versioned same-contract alternative: keeps the v5 hidden-state policy and
// identity/ticket binding, removes the masked-moment relation, and binds both
// roles' retained one-hot vectors through per-role Poseidon commitments.
// Each role's commitment covers (2N+role, blind, context, share). The circuit
// does not range-check a share to 128 bits; canonicality is enforced by the
// receiver's byte decoder and by commitment binding (see CONTRACT.md).
template VectorBindingV6(N) {
    var Q = 340282366920938462946865773367900766209;
    signal input commitment[2];
    signal input context[2];
    signal input bit;
    signal input primary;
    signal input blind[2];
    signal input share[2][N];
    signal input carry[N];
    signal selected_index;
    bit * (bit - 1) === 0;
    component range = LessThan(14);
    range.in[0] <== primary;
    range.in[1] <== N-1;
    range.out === 1;
    selected_index <== (N-1) + bit * (primary - (N-1));
    component eq[N];
    for (var i=0; i<N; i++) {
        eq[i] = IsEqual();
        eq[i].in[0] <== selected_index;
        eq[i].in[1] <== i;
        carry[i] * (carry[i]-1) === 0;
        share[0][i] + share[1][i] === eq[i].out + carry[i]*Q;
    }
    component initial[2];
    component folds[2][(N+14)\15];
    signal accumulator[2][(N+14)\15+1];
    for (var role=0; role<2; role++) {
        initial[role] = Poseidon(4);
        initial[role].inputs[0] <== 2*N+role;
        initial[role].inputs[1] <== blind[role];
        initial[role].inputs[2] <== context[0];
        initial[role].inputs[3] <== context[1];
        accumulator[role][0] <== initial[role].out;
        for (var block=0; block<(N+14)\15; block++) {
            folds[role][block] = Poseidon(16);
            folds[role][block].inputs[0] <== accumulator[role][block];
            for (var j=0; j<15; j++) {
                if (block*15+j<N) folds[role][block].inputs[j+1] <== share[role][block*15+j];
                else folds[role][block].inputs[j+1] <== 0;
            }
            accumulator[role][block+1] <== folds[role][block].out;
        }
        accumulator[role][(N+14)\15] === commitment[role];
    }
}

template Alternative(N) {
    signal input relation_version;
    signal input c_prev_x;
    signal input c_prev_y;
    signal input c_next_x;
    signal input c_next_y;
    signal input c_ticket_x;
    signal input c_ticket_y;
    signal input c_k_anchor_x;
    signal input c_k_anchor_y;
    signal input anchor_prev_x;
    signal input anchor_prev_y;
    signal input anchor_next_x;
    signal input anchor_next_y;
    signal input key_tag_96;
    signal input rid_128;
    signal input ctx_limb_hi;
    signal input ctx_limb_lo;
    signal input contribution_bit;
    signal input vector_commitment[2];
    signal input receipt_commitment[2];
    signal input cells[3][2]; signal input remainders[3][2]; signal input coords[3][2];
    signal input rho_state[3];
    signal input payload_cell[2]; signal input payload_rem[2];
    signal input rho_ticket;
    signal input rho_receipt[2];
    signal input vector_blind[2];
    signal input vector_share[2][N];
    signal input vector_carry[N];
    relation_version === 6;
    component state[3]; component com[3];
    for (var i=0; i<3; i++) {
        state[i] = State(); state[i].cell <== cells[i]; state[i].rem <== remainders[i]; state[i].xy <== coords[i];
        com[i] = Commit(40, G_STATE(), H_STATE()); com[i].message <== state[i].message; com[i].rho <== rho_state[i];
    }
    c_prev_x === com[0].point[0];
    c_prev_y === com[0].point[1];
    c_next_x === com[1].point[0];
    c_next_y === com[1].point[1];
    c_k_anchor_x === com[2].point[0];
    c_k_anchor_y === com[2].point[1];
    anchor_prev_x === c_prev_x;
    anchor_prev_y === c_prev_y;
    anchor_next_x === c_next_x;
    anchor_next_y === c_next_y;
    component step = Distance(144000000);
    step.current <== coords[1]; step.reference <== coords[0];
    component anchor = Distance(10890000);
    anchor.current <== coords[1]; anchor.reference <== coords[2];
    for (var i=0; i<2; i++) {
        payload_cell[i] === cells[1][i];
        payload_rem[i] === remainders[1][i];
    }
    contribution_bit * (contribution_bit - 1) === 0;
    signal cell_index <== cells[1][1]*100 + cells[1][0];
    component rid = Num2Bits(128); rid.in <== rid_128;
    component kh = Num2Bits(96); kh.in <== key_tag_96;
    component ctx[2];
    ctx[0] = Num2Bits(128); ctx[0].in <== ctx_limb_hi;
    ctx[1] = Num2Bits(128); ctx[1].in <== ctx_limb_lo;
    component ticket = Commit(224, G_TICKET(), H_TICKET());
    ticket.message <== key_tag_96*340282366920938463463374607431768211456 + rid_128;
    ticket.rho <== rho_ticket;
    c_ticket_x === ticket.point[0];
    c_ticket_y === ticket.point[1];
    // Receipt binding: h = Poseidon(role, cv, ctx_hi, ctx_lo);
    // receipt = Poseidon(h, rid, bit, rho_receipt). The service must sign the
    // same (role, cv, ctx, rid, bit) tuple.
    component hbind[2]; component rbind[2];
    for (var role=0; role<2; role++) {
        hbind[role] = Poseidon(4);
        hbind[role].inputs[0] <== role;
        hbind[role].inputs[1] <== vector_commitment[role];
        hbind[role].inputs[2] <== ctx_limb_hi;
        hbind[role].inputs[3] <== ctx_limb_lo;
        rbind[role] = Poseidon(4);
        rbind[role].inputs[0] <== hbind[role].out;
        rbind[role].inputs[1] <== rid_128;
        rbind[role].inputs[2] <== contribution_bit;
        rbind[role].inputs[3] <== rho_receipt[role];
        receipt_commitment[role] === rbind[role].out;
    }
    component vector = VectorBindingV6(N);
    vector.commitment <== vector_commitment;
    vector.context[0] <== ctx_limb_hi;
    vector.context[1] <== ctx_limb_lo;
    vector.bit <== contribution_bit;
    vector.primary <== cell_index;
    vector.blind <== vector_blind;
    vector.share <== vector_share;
    vector.carry <== vector_carry;
}
