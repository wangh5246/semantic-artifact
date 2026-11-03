# Six-delta degree enumeration (final v3)

2026-11-01. This completes the degree enumeration after the local review's
six-delta correction. The actual old keys are now read (K2 v3), so the source
columns are actual, not structural bounds.

## Term classes and maximum degrees

`k=6` independent deltas: `Delta_1..Delta_4` (pot14: current genesis, current
transition, historical genesis, N8) and `Delta_5,Delta_6` (pot22 old/new
D=10001). The common denominator is `D=product_{r=1..6} Delta_r`.

| term class | G1 maximum after multiplying by D | G2 |
| --- | ---: | ---: |
| pot14 raw G1 `X^i` (i≤32,766), alpha/beta (i≤16,383) | 32,766+6=32,772; alpha/beta 16,383+6=16,389 | raw G2 16,383 |
| pot22 raw G1 `X'^i` (i≤8,388,606), alpha'/beta' (prepared) | 8,388,606+6=8,388,612 | raw G2 4,194,303 |
| initial/final key public q/u/v and private q/Delta, K/Delta, H/Delta | M+k−1 ≤ 1,048,576+5=1,048,581; delta positive 1+6=7 | v_i/Delta: 1,048,576; delta 1; contribution 2 |
| contribution PoK | 2+6=8 | 2 |
| source `S_i` numerator max(2,n_r) + k−1 | 1,048,576+5=1,048,581 | source nu degree 1 |
| new independent Z / PoK | 1+6=7 / 2+6=8 | 1 / 2 |
| vkey alpha beta | 2 | 2 |

Every G1 term is at most `8,388,612`; every G2 term at most `4,194,303`.
Therefore, using G4b §6,

```
D1 = max(L1+k, M+k-1) = max(8,388,606+6, 1,048,576+5) = 8,388,612
D2 = L2 = 4,194,303
DT = max(D1+L2, D1+1, max_r n_r+k, 2+k)
   = max(12,582,915, 8,388,613, 1,048,582, 8) = 12,582,915
```

The v2 `8,388,609 / 12,582,912` used the k=3 `+3`; it is corrected here.
The local review's worked term `X22^8,388,606 * product_j Delta_j` has degree
8,388,612; the G2 raw term gives the GT 12,582,915. No source class in the
actual v3 inventory exceeds these maxima: the pot22 ptau/keys are the
dominant raw/prepared columns; N8 and v5 terms are smaller; contribution
transcripts are degree 2; source numerators are bounded by the D10001 domain.

This enumeration covers all term classes in the source normal form J1-J2. It
is a **proved degree bound for the declared v3 source inventory**, not a
certification of an unlisted future key or a different ceremony. The budget
formulas/arithmetic are in `budget-v3.json`.
