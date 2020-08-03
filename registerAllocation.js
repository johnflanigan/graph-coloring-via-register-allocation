/**
 * Represents an instruction.
 */
class Instruction {
  /**
   * @constructor
   * @param {string} opcode - instruction opcode.
   * @param {Def[]} def - outputs.
   * @param {Use[]} use - inputs.
   */
  constructor(opcode, def, use) {
    this.opcode = opcode;
    this.def = def;
    this.use = use;
  }
}

/**
 * Represents outputs.
 */
class Def {
  /**
   * @constructor
   * @param {string} reg - a symbolic register.
   * @param {boolean} dead - indicates whether or not reg goes dead.
   */
  constructor(reg, dead) {
    this.reg = reg;
    this.dead = dead;
  }
}

/**
 * Represents inputs.
 */
class Use {
  /**
   * @constructor
   * @param {string} reg - a symbolic register.
   * @param {boolean} dead - indicates whether or not reg goes dead.
   */
  constructor(reg, dead) {
    this.reg = reg;
    this.dead = dead;
  }
}

// il is an ordered sequence of instructions
let il;

// register interference graph = set of edges
// each edge being specified by the set of its endpoints
let graph;

// set of available colors (machine registers)
let colors;

// gives estimated cost of spilling each symbolic register
let cost;

// set of spilled symbolic registers
let spilled;

/**
 * Build graph, coalesce, and color
 */
function colorIl() {
  buildGraph();
  coalesceNodes();
  const coloring = colorGraph(graph, registersInIl());
  if (coloring === undefined) {
    return coloring;
  }
  rewriteIl(coloring);
  return coloring;
}

/**
 * Build the register interference graph
 */
function buildGraph(il) {
  const graph = new Set();
  const liveness = new Map();

  for (const {opcode, def, use} of il) {
    if (opcode === 'bb') {
      def.filter(({dead}) => !dead).map(({reg}) => {
        if (liveness.has(reg)) {
          liveness.set(reg, liveness.get(reg) + 1);
        } else {
          liveness.set(reg, 1);
        }
      });
    } else {
      use.filter(({dead}) => dead).map(({reg}) => {
        liveness.set(reg, liveness.get(reg) - 1);
        if (liveness.get(reg) === 0) {
          liveness.delete(reg);
        }
      });
      def.map(({reg, dead}) => {
        liveness.forEach(((value, key) => {
          if (key !== reg) {
            graph.add({'source': reg, 'target': key});
          }
        }));
        if (!dead) {
          if (liveness.has(reg)) {
            liveness.set(reg, liveness.get(reg) + 1);
          } else {
            liveness.set(reg, 1);
          }
        }
      });
    }
  }

  return graph;
}

/**
 * Coalesce away copy operations
 */
function coalesceNodes() {

}

/**
 * Color the graph with edges g and nodes n
 * @param {} g - edges
 * @param {} n - nodes
 */
function colorGraph(g, n) {
  return undefined;
}

/**
 * Estimate cost of spilling each register
 */
function estimateSpillCosts() {

}

/**
 * Make spill decisions
 */
function decideSpills() {

}

/**
 * Insert spill and reload instructions
 */
function insertSpillCode() {

}

/**
 * Apply function f to each register in il
 * @param f function
 */
function rewriteIl(f) {

}

/**
 * Returns set of symbolic registers in il
 */
function registersInIl() {

}

/**
 * @param x node
 * @param g set of edges
 */
function neighbors(x, g) {

}

module.exports = {Instruction, Def, Use, buildGraph};
