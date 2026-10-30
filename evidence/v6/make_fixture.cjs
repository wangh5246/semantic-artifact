// Deterministic v6 fixture builder. Same Pedersen parameters as v5, plus the
// versioned Poseidon vector/receipt commitments. No native service is touched.
'use strict';
const fs = require('fs');
const path = require('path');

const REPO = process.env.V6_ROOT ? path.resolve(process.env.V6_ROOT) : path.resolve(__dirname, '../../..');
const PACKAGE = path.join(REPO, 'research/w1-w5-native-profile-2026-10-17');
const KERNELS = path.join(REPO, 'research/controller-and-sharding-comparison-2026-10-24/actual-binding-r1/kernels');
const profile = JSON.parse(fs.readFileSync(path.join(PACKAGE, 'contract/profile.json')));
const gens = JSON.parse(fs.readFileSync(path.join(PACKAGE, 'circuits/generators-v5.json'))).generators;
// JSON.parse loses precision on these integers; use the exact standard values.
const P = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const L = 2736030358979909402780800718157159386076813972158567259200215660948447373041n;
const Q = 340282366920938462946865773367900766209n;

const mod = (x, m = P) => ((x % m) + m) % m;
const inv = (x) => {
  let r = 1n, b = mod(x), e = P - 2n;
  while (e > 0n) { if (e & 1n) r = r * b % P; b = b * b % P; e >>= 1n; }
  return r;
};
function add(p, q) {
  const [x, y, z] = p, [u, v, w] = q;
  const a = mod(z * w), b = mod(a * a), c = mod(x * u), d = mod(y * v);
  const e = mod(168696n * c * d), f = mod(b - e), g = mod(b + e);
  return [mod(a * f * (mod((x + y) * (u + v)) - c - d)), mod(a * g * (d - 168700n * c)), mod(f * g)];
}
function mul(base, n) {
  if (n < 0n) throw Error('negative scalar');
  let out = [0n, 1n, 1n];
  for (const bit of n.toString(2)) {
    out = add(out, out);
    if (bit === '1') out = add(out, [base[0], base[1], 1n]);
  }
  return out;
}
function commit(m, rho, kind) {
  if (process.env.V6_DEBUG) console.error('commit', kind, String(m), String(rho), gens['g_' + kind].generator[0].slice(0, 8));
  const p = add(mul(gens['g_' + kind].generator.map(BigInt), m), mul(gens['h_' + kind].generator.map(BigInt), rho));
  if (process.env.V6_DEBUG) console.error('sum', p.map(String).join(','));
  if (p[2] === 0n) throw Error('invalid point');
  const zi = inv(p[2]);
  if (process.env.V6_DEBUG) console.error('inv', String(zi));
  return [mod(p[0] * zi), mod(p[1] * zi)];
}
function det(seed, bound) { // deterministic non-secret fixture values
  let h = 0xcbf29ce484222325n;
  const s = String(seed);
  for (let i = 0; i < s.length; i++) { h ^= BigInt(s.charCodeAt(i)); h = mod(h * 0x100000001b3n, 1n << 64n); }
  return h % bound;
}

const cache = {};
async function poseidon(kind, inputs) {
  if (!cache[kind]) {
    const dir = path.join(KERNELS, kind, kind + '_js');
    cache[kind] = await require(path.join(dir, 'witness_calculator.js'))(fs.readFileSync(path.join(dir, kind + '.wasm')));
  }
  return (await cache[kind].calculateWitness({ inputs: inputs.map(String) }, 1))[1];
}
async function vectorCommitment(N, role, blind, context, shares) {
  let acc = await poseidon('poseidon4', [BigInt(2 * N + role), blind, ...context]);
  for (let i = 0; i < N; i += 15) {
    const block = shares.slice(i, i + 15).map(BigInt);
    while (block.length < 15) block.push(0n);
    acc = await poseidon('poseidon16', [acc, ...block]);
  }
  return acc;
}
async function receiptCommitment(role, cv, context, rid, bit, rho) {
  const h = await poseidon('poseidon4', [BigInt(role), cv, ...context]);
  return poseidon('poseidon4', [h, rid, BigInt(bit), rho]);
}

async function main() {
  const argv = process.argv.slice(2);
  const opt = { N: 8, out: 'input.json', bit: 1, seed: 1, state: 'small' };
  for (let i = 0; i < argv.length; i += 2) {
    const k = argv[i].replace(/^--/, '');
    opt[k] = k === 'N' || k === 'bit' || k === 'seed' ? Number(argv[i + 1]) : argv[i + 1];
  }
  const N = opt.N;
  // Small N uses a real grid cell whose histogram index is < N-1.
  const coords = opt.state === 'real'
    ? [[1000, 1000], [1050, 1050], [1000, 1000]]
    : [[500, 0], [505, 5], [500, 0]];
  const [prevXY, nextXY, anchorXY] = coords;
  const mkState = (xy, s) => {
    const rho = det('rho-state-' + s + '-' + opt.seed, L);
    const point = commit(BigInt(xy[0]) * 1048576n + BigInt(xy[1]), rho, 'state');
    if (process.env.V6_DEBUG) console.error('state', s, rho.toString(), point.map(String).join(','));
    return { xy, cell: [Math.floor(xy[0] / 100), Math.floor(xy[1] / 100)], rem: [xy[0] % 100, xy[1] % 100], rho, point };
  };
  const prev = mkState(prevXY, 0), nxt = mkState(nextXY, 1), anchor = mkState(anchorXY, 2);
  const index = nxt.cell[1] * 100 + nxt.cell[0];
  if (index >= N - 1) throw Error('STATE_INDEX_OUT_OF_REDUCED_RANGE:' + index);
  const selected = opt.bit ? index : N - 1;
  const shares = [[], []];
  const carry = [];
  for (let i = 0; i < N; i++) {
    const a = det('share-' + i + '-' + opt.seed, Q);
    const eq = i === selected ? 1n : 0n;
    const b = mod(eq - a, Q);
    const c = a + b === eq ? 0n : 1n;
    if (a + b !== eq + c * Q) throw Error('RECONSTRUCTION');
    shares[0].push(a); shares[1].push(b); carry.push(c);
  }
  const context = [101n, 202n];
  const blind = [det('blind-a-' + opt.seed, P), det('blind-r-' + opt.seed, P)];
  const rhoReceipt = [det('receipt-a-' + opt.seed, L), det('receipt-r-' + opt.seed, L)];
  const keyTag = 9876543210123456789n, rid = 11n;
  const rhoTicket = det('ticket-' + opt.seed, L);
  const cv = [await vectorCommitment(N, 0, blind[0], context, shares[0]),
              await vectorCommitment(N, 1, blind[1], context, shares[1])];
  const rc = [await receiptCommitment(0, cv[0], context, rid, opt.bit, rhoReceipt[0]),
              await receiptCommitment(1, cv[1], context, rid, opt.bit, rhoReceipt[1])];
  const ticket = commit(keyTag * (1n << 128n) + rid, rhoTicket, 'ticket');
  const input = {
    relation_version: 6, key_tag_96: keyTag, rid_128: rid,
    ctx_limb_hi: context[0], ctx_limb_lo: context[1], contribution_bit: opt.bit,
    cells: [prev.cell, nxt.cell, anchor.cell],
    remainders: [prev.rem, nxt.rem, anchor.rem],
    coords: [prev.xy, nxt.xy, anchor.xy],
    rho_state: [prev.rho, nxt.rho, anchor.rho],
    payload_cell: nxt.cell, payload_rem: nxt.rem,
    rho_ticket: rhoTicket, rho_receipt: rhoReceipt,
    vector_blind: blind, vector_share: shares, vector_carry: carry,
    vector_commitment: cv, receipt_commitment: rc,
    c_prev_x: prev.point[0], c_prev_y: prev.point[1],
    c_next_x: nxt.point[0], c_next_y: nxt.point[1],
    c_k_anchor_x: anchor.point[0], c_k_anchor_y: anchor.point[1],
    anchor_prev_x: prev.point[0], anchor_prev_y: prev.point[1],
    anchor_next_x: nxt.point[0], anchor_next_y: nxt.point[1],
    c_ticket_x: ticket[0], c_ticket_y: ticket[1],
  };
  const stringify = (v) => {
    if (typeof v === 'bigint') return v.toString();
    if (typeof v === 'number' && Number.isSafeInteger(v)) return String(v);
    if (Array.isArray(v)) return v.map(stringify);
    if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v)) o[k] = stringify(v[k]); return o; }
    return v;
  };
  fs.writeFileSync(opt.out, JSON.stringify(stringify(input), null, 2) + '\n');
  fs.writeFileSync(opt.out + '.meta.json', JSON.stringify({ N, bit: opt.bit, selected, cell_index: index, scope: 'reduced-dimension' }, null, 2) + '\n');
  console.log(JSON.stringify({ out: opt.out, N, bit: opt.bit, selected }));
}
main().catch((e) => { console.error(e.stack || e); process.exitCode = 1; });
