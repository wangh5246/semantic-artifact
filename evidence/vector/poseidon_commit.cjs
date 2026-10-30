// Shared Poseidon helpers for the vector fixture/validator. Uses the pinned
// circomlib kernels from the earlier comparator component tests.
'use strict';
const fs = require('fs');
const path = require('path');
const PACKAGE = process.env.VECTOR_ROOT ? path.resolve(process.env.VECTOR_ROOT) : path.resolve(__dirname, '../../..');
const KERNELS = path.join(PACKAGE, 'research/controller-and-sharding-comparison-2026-10-24/actual-binding-r1/kernels');
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
module.exports = { poseidon, vectorCommitment, receiptCommitment };
