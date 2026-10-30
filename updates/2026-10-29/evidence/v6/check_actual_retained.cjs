// Receiver-path check over the actual retained aggregate bytes of a native run.
// This is the exported collection payload (sum of the eight per-report output
// shares), not a per-report share; the one-hot relation is exercised separately.
'use strict';
const fs = require('fs');
const crypto = require('crypto');
const { vectorCommitment } = require('./poseidon_commit.cjs');

const Q = 340282366920938462946865773367900766209n;
const P = 21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const N = 10001;
const CONTEXT = [101n, 202n];
function det(seed) {
  let h = 0xcbf29ce484222325n;
  for (const ch of String(seed)) { h ^= BigInt(ch.charCodeAt(0)); h = (h * 0x100000001b3n) % (1n << 64n); }
  return h % P;
}
function decode(hex) {
  const b = Buffer.from(hex, 'hex');
  if (b.length !== 16 * N) throw Error('LENGTH:' + b.length);
  const out = [];
  for (let i = 0; i < N; i++) {
    let v = 0n;
    for (let j = 15; j >= 0; j--) v = (v << 8n) + BigInt(b[16 * i + j]);
    out.push(v);
  }
  return { bytes: b, values: out };
}
function decodeCanonical(hex) {
  const d = decode(hex);
  if (d.values.some((v) => v >= Q)) throw Error('NONCANONICAL_FIELD');
  return d;
}
(async () => {
  const argv = process.argv.slice(2);
  const opt = { run: '', out: '', label: '' };
  for (let i = 0; i < argv.length; i += 2) { const k = argv[i].replace(/^--/, ''); opt[k] = argv[i + 1]; }
  const ev = JSON.parse(fs.readFileSync(opt.run));
  const roles = ['leader', 'helper'];
  const results = [];
  const payloads = {};
  for (const role of roles) {
    const hex = ev.after[role].payload[0].payload_hex;
    payloads[role] = hex;
    const { bytes, values } = decodeCanonical(hex);
    const blind = det('actual-blind-' + role);
    const cv = await vectorCommitment(N, roles.indexOf(role), blind, CONTEXT, values);
    const cv2 = await vectorCommitment(N, roles.indexOf(role), blind, CONTEXT, values);
    const flip = Buffer.from(bytes); flip[0] ^= 1;
    const cvFlip = await vectorCommitment(N, roles.indexOf(role), blind, CONTEXT, decode(flip.toString('hex')).values);
    const cvWrongRole = await vectorCommitment(N, 1 - roles.indexOf(role), blind, CONTEXT, values);
    const cvWrongCtx = await vectorCommitment(N, roles.indexOf(role), blind, [102n, 202n], values);
    results.push({ role, bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
      canonical: true, commitment: cv.toString(), deterministic: cv === cv2,
      byte_flip_changes: cvFlip !== cv, wrong_role_changes: cvWrongRole !== cv, wrong_context_changes: cvWrongCtx !== cv });
  }
  const bad = Buffer.alloc(16 * N, 0xff);
  let noncanonicalRejected = false;
  try { decodeCanonical(bad.toString('hex')); } catch (e) { noncanonicalRejected = e.message === 'NONCANONICAL_FIELD'; }
  const a = decode(payloads.leader).values, b = decode(payloads.helper).values;
  const sum = a.map((x, i) => (x + b[i]) % Q);
  const report = {
    label: opt.label, source: opt.run,
    payloads: results,
    receiver_decoder_rejects_noncanonical: noncanonicalRejected,
    reconstruction: { nonzero_cells: sum.filter((x) => x !== 0n).length, total_mass: sum.reduce((acc, x) => acc + x, 0n).toString() },
    scope: 'actual native retained aggregate bytes; receiver-side decode/commitment and negative controls; not per-report share and not live Janus path'
  };
  fs.writeFileSync(opt.out, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ label: opt.label, ...report.reconstruction, noncanonical_rejected: noncanonicalRejected }));
})().catch((e) => { console.error(e.stack || e); process.exitCode = 1; });
