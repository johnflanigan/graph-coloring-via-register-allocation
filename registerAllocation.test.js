import {test} from '@jest/globals';

const registerAllocation = require('./registerAllocation');
const {Instruction, Def, Use} = require('./registerAllocation');

test('build graph', () => {
  il = [
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
    new Instruction('op3', [
      new Def('b', false),
    ], [
      new Use('c', true),
    ]),
    new Instruction('ret', [], [
      new Use('a', true),
      new Use('b', true),
    ]),
  ];

  registerAllocation.buildGraph(il);

  expect(graph).toBe(3);
});
