// const registerAllocation = require('./registerAllocation');
const {Instruction, Def, Use, buildGraph, coalesceNodes} = require('./registerAllocation');

test('build graph', () => {
  let il = [
    new Instruction('bb', [
      new Def('a', false),
    ], []),
    new Instruction('op1', [
      new Def('b', false),
    ], [
      new Use('a', false),
    ]),
    new Instruction('op2', [
      new Def('c', false),
    ], [
      new Use('b', true),
    ]),
    new Instruction('copy', [
      new Def('d', false),
    ], [
      new Use('c', true),
    ]),
    new Instruction('op3', [
      new Def('b', false),
    ], [
      new Use('d', true),
    ]),
    new Instruction('ret', [], [
      new Use('a', true),
      new Use('b', true),
    ]),
  ];

  const graph = buildGraph(il);

  expect(graph).toBe(3);
});

test('coalesce nodes', () => {
  const il = [
    new Instruction('bb', [
      new Def('a', false),
    ], []),
    new Instruction('op1', [
      new Def('b', false),
    ], [
      new Use('a', false),
    ]),
    new Instruction('op2', [
      new Def('c', false),
    ], [
      new Use('b', true),
    ]),
    new Instruction('copy', [
      new Def('d', false),
    ], [
      new Use('c', true),
    ]),
    new Instruction('op3', [
      new Def('b', false),
    ], [
      new Use('d', true),
    ]),
    new Instruction('ret', [], [
      new Use('a', true),
      new Use('b', true),
    ]),
  ];

  const graph = new Set([
    {'source': 'b', 'target': 'a'},
    {'source': 'c', 'target': 'a'},
    {'source': 'd', 'target': 'a'},
  ]);

  const {coalescedIl, coalescedGraph} = coalesceNodes(il, graph);

  expect(coalescedIl).toBe(3);
  expect(coalescedGraph).toBe(3);
});
