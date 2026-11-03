# SHTPC Circuit Specifications and Kernels

This directory provides the circuit specifications, relations, and verification kernels for SHTPC (Stateful History-to-Payload Closure).

## 1. State Transition Circuit (`hadwc_transition_v5.circom`)
Enforces admissible trajectory dynamics and binds state commitments to aggregate contributions (Section 3.3).

### Ordered Public Signals (25 signals)
1. `relation_version`: Protocol version tag (`=== 5`).
2. `c_a_x`, `c_a_y`: Pedersen commitment to active anchor.
3. `c_r_x`, `c_r_y`: Pedersen commitment to payload coordinates.
4. `c_prev_x`, `c_prev_y`: Pedersen commitment to predecessor state.
5. `c_next_x`, `c_next_y`: Pedersen commitment to successor state.
6. `c_ticket_x`, `c_ticket_y`: Pedersen commitment to ticket.
7. `c_receipt_x`, `c_receipt_y`: Pedersen commitment to receipt.
8. `anchor_prev_x`, `anchor_prev_y`: Predecessor anchor coordinates.
9. `anchor_next_x`, `anchor_next_y`: Successor anchor coordinates.
10. `key_tag_96`: 96-bit key-binding tag.
11. `masked_native_index`: One-hot index offset into native bucket space.
12. `contribution_bit`: Boolean validity flag ($b \in \{0, 1\}$).
13. `rid_128`: 128-bit report context identifier.
14. `ctx_limb_hi`, `ctx_limb_lo`: Two 64-bit limbs binding the sampling context.
15. `c_k_anchor_x`, `c_k_anchor_y`: Pedersen commitment to $K$-anchor point.

### Enforced Constraints
- Spatial Grid Mapping: $p = \mathsf{Grid}(\mathbf{x}_r)$.
- Velocity Tier Drift: $\|\mathbf{x}_r - \mathbf{x}_{\rm prev}\|^2 \le \tau_u^2 \Delta t_t^2$.
- Anchor Distance Cap: $\|\mathbf{x}_r - \mathbf{a}_t\|^2 \le \min\{\tau_u^2 (\Delta T_t^{(K)})^2, c_{\rm policy}^2\}$.
- Cross-Field Canonical Consistency: Enforces $x + r_A + r_B = T + \chi q$ with carry $\chi \in \{0, 1, 2\}$.

## 2. Common Primitives (`hadwc_common_v5.circom`)
Pedersen commitments, multiplexers, and 40/64-bit range checkers.

## 3. Vector Commitment Comparison Kernels
- `poseidon4.circom`, `poseidon16.circom`: Poseidon sponge permutations.
- `keccak12.circom`: Keccak round compression.
- `share_row.circom`: Secret-share evaluation.
- `check_r1cs_v2.cpp`: C++ streaming R1CS checker.
- `compose_r2.py`: Multi-bin binding generator.
