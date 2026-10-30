// v6 combined-witness positive/negative controls. Runs the actual wasm/r1cs.
'use strict';
const fs = require('fs');
const path = require('path');


const PACKAGE = process.env.V6_ROOT ? path.resolve(process.env.V6_ROOT) : path.resolve(__dirname, '../../..');
const gens = JSON.parse(fs.readFileSync(path.join(PACKAGE, 'research/w1-w5-native-profile-2026-10-17/circuits/generators-v5.json'))).generators;
const P = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const L = 2736030358979909402780800718157159386076813972158567259200215660948447373041n;
const Q = 340282366920938462946865773367900766209n;
const mod = (x, m = P) => ((x % m) + m) % m;
function inv(x) { let r = 1n, b = mod(x), e = P - 2n; while (e > 0n) { if (e & 1n) r = r * b % P; b = b * b % P; e >>= 1n; } return r; }
function add(p, q) {
  const [x, y, z] = p, [u, v, w] = q;
  const a = mod(z * w), b = mod(a * a), c = mod(x * u), d = mod(y * v);
  const e = mod(168696n * c * d), f = mod(b - e), g = mod(b + e);
  return [mod(a * f * (mod((x + y) * (u + v)) - c - d)), mod(a * g * (d - 168700n * c)), mod(f * g)];
}
function mul(base, n) { let out = [0n, 1n, 1n]; for (const bit of n.toString(2)) { out = add(out, out); if (bit === '1') out = add(out, [base[0], base[1], 1n]); } return out; }
function commit(m, rho, kind) { const p = add(mul(gens['g_' + kind].generator.map(BigInt), m), mul(gens['h_' + kind].generator.map(BigInt), rho)); const zi = inv(p[2]); return [mod(p[0] * zi), mod(p[1] * zi)]; }
const clone = (x) => JSON.parse(JSON.stringify(x));
let snarkjs = null;
const big = (x) => BigInt(x);
const S = (x) => String(x);

function setState(inp, s, xy) {
  const cell = [Math.floor(xy[0] / 100), Math.floor(xy[1] / 100)];
  const rem = [xy[0] % 100, xy[1] % 100];
  inp.coords[s] = xy; inp.cells[s] = cell; inp.remainders[s] = rem;
  const pt = commit(big(xy[0]) * 1048576n + big(xy[1]), big(inp.rho_state[s]), 'state');
  const names = [['c_prev', 'anchor_prev'], ['c_next', 'anchor_next'], ['c_k_anchor']][s];
  for (const n of names) { inp[n + '_x'] = S(pt[0]); inp[n + '_y'] = S(pt[1]); }
  if (s === 1) { inp.payload_cell = cell; inp.payload_rem = rem; }
}

function main() {
  const argv = process.argv.slice(2);
  const opt = { base: 'build8/input-bit1.json', base0: 'build8/input-bit0.json', wasm: 'build8/v6_main_8_js/v6_main_8.wasm', r1cs: 'build8/v6_main_8.r1cs', out: 'build8/witness-checks.json', n: 8, snarkjs: process.env.SNARKJS_MODULE || '/usr/local/lib/node_modules/snarkjs' };
  for (let i = 0; i < argv.length; i += 2) { const k = argv[i].replace(/^--/, ''); opt[k] = k === 'n' ? Number(argv[i + 1]) : argv[i + 1]; }
  const base1 = JSON.parse(fs.readFileSync(opt.base));
  const base0 = JSON.parse(fs.readFileSync(opt.base0));
  const N = opt.n;
  const cases = [];
  const addCase = (name, inp, expect, note) => cases.push({ name, input: S2(inp), expect_accept: expect, note });

  addCase('valid-bit1', clone(base1), true, 'positive one contribution');
  addCase('valid-bit0', clone(base0), true, 'zero contribution uses sentinel');
  {
    const c = clone(base1); c.vector_share[0][0] = S(big(c.vector_share[0][0]) + 1n);
    addCase('share-tamper', c, false, 'one coordinate no longer reconstructs one-hot');
  }
  {
    const c = clone(base1); c.contribution_bit = 0;
    addCase('bit-flip', c, false, 'bit flip changes selected index without changing shares');
  }
  {
    const c = clone(base1); [c.vector_commitment[0], c.vector_commitment[1]] = [c.vector_commitment[1], c.vector_commitment[0]];
    addCase('role-swap', c, false, 'role is in the commitment domain');
  }
  {
    const c = clone(base1); c.ctx_limb_lo = S(big(c.ctx_limb_lo) + 1n);
    addCase('context-tamper', c, false, 'context enters vector and receipt commitments');
  }
  {
    const c = clone(base1); c.receipt_commitment[0] = S(big(c.receipt_commitment[0]) + 1n);
    addCase('receipt-tamper', c, false, 'receipt commitment is publicly checked');
  }
  {
    const c = clone(base1); c.rid_128 = S(big(c.rid_128) + 1n);
    addCase('cross-report-rid', c, false, 'rid enters ticket and receipt commitments');
  }
  {
    const c = clone(base1); c.c_ticket_x = S(big(c.c_ticket_x) + 1n);
    addCase('ticket-tamper', c, false, 'ticket commitment is checked');
  }
  {
    const c = clone(base1); c.c_prev_x = S(big(c.c_prev_x) + 1n);
    addCase('state-tamper', c, false, 'previous state commitment is checked');
  }
  {
    const c = clone(base1);
    // Move the hidden cell and re-commit the state, keeping the old one-hot share.
    const newXY = N === 8 ? [605, 0] : [1150, 1150];
    setState(c, 1, newXY);
    addCase('wrong-cell-recommitted', c, false, 'state re-commits a different cell; retained vector still selects the old cell');
  }
  {
    const c = clone(base1);
    // Policy violation: next point far from the anchor, state consistently re-committed.
    if (N > 8) {
      setState(c, 1, [9000, 9000]);
      setState(c, 0, [0, 0]);
      addCase('distance-policy', c, false, 'distance cap violation');
    }
  }
  {
    const c = clone(base0);
    const newXY = N === 8 ? [605, 0] : [1150, 1150];
    setState(c, 1, newXY);
    addCase('zero-bit-primary-change', c, true, 'sentinel semantics: zero contribution does not claim a cell');
  }
  {
    const c = clone(base1);
    // Noncanonical share pair: circuit accepts, receiver byte decoder rejects.
    const sel = Number(c.contribution_bit) ? Number(c.cells[1][1]) * 100 + Number(c.cells[1][0]) : N - 1;
    for (let i = 0; i < N; i++) {
      const eq = i === sel ? 1n : 0n;
      c.vector_share[0][i] = S(eq + Q);
      c.vector_share[1][i] = '0';
      c.vector_carry[i] = '1';
    }
    const { vectorCommitment, receiptCommitment } = require('./poseidon_commit.cjs');
    const ctx = [big(c.ctx_limb_hi), big(c.ctx_limb_lo)];
    (async () => {
      c.vector_commitment[0] = S(await vectorCommitment(N, 0, big(c.vector_blind[0]), ctx, c.vector_share[0].map(big)));
      c.vector_commitment[1] = S(await vectorCommitment(N, 1, big(c.vector_blind[1]), ctx, c.vector_share[1].map(big)));
      for (const role of [0, 1]) {
        c.receipt_commitment[role] = S(await receiptCommitment(role, big(c.vector_commitment[role]), ctx, big(c.rid_128), 1, big(c.rho_receipt[role])));
      }
      addCase('noncanonical-share-circuit', c, true, 'circuit accepts Q+1; canonical check is a receiver obligation');
      await finish(cases, opt);
    })().catch((e) => { console.error(e); process.exitCode = 1; });
    return;
  }
  finish(cases, opt);
}

async function finish(cases, opt) {
  const runDir = path.dirname(path.resolve(opt.wasm));
  const tmp = path.join(runDir, 'tmp-witness');
  fs.mkdirSync(tmp, { recursive: true });
  snarkjs = require(opt.snarkjs);
  const results = [];
  for (const c of cases) {
    const inp = path.join(tmp, c.name + '.json');
    const wtns = path.join(tmp, c.name + '.wtns');
    fs.writeFileSync(inp, c.input + '\n');
    let accepted = false, diagnostic = null;
    const input = JSON.parse(c.input);
    try {
      const w = { type: 'mem' };
      await snarkjs.wtns.calculate(input, opt.wasm, w);
      accepted = await snarkjs.wtns.check(opt.r1cs, w);
    } catch (e) { diagnostic = String(e.message || e).slice(0, 300); }
    results.push({ case: c.name, expect_accept: c.expect_accept, accepted, passed: accepted === c.expect_accept, note: c.note, diagnostic });
    fs.unlinkSync(inp);
  }
  const report = { all_passed: results.every((x) => x.passed), N: opt.n, cases: results, scope: 'actual v6 wasm/r1cs witness; no proof or native service' };
  fs.writeFileSync(opt.out, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ all_passed: report.all_passed, cases: results.length }));
  process.exit(report.all_passed ? 0 : 1);
}
function S2(inp) { return JSON.stringify(inp); }
main();
