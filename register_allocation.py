from random import choice
from typing import List


class Dec:
    def __init__(self, reg: str, dead: bool):
        self.reg = reg
        self.dead = dead


class Use:
    def __init__(self, reg: str, dead: bool):
        self.reg = reg
        self.dead = dead


class Instruction:
    def __init__(self, opcode: str, dec: List[Dec], use: List[Use], frequency=1):
        self.opcode = opcode
        self.dec = dec
        self.use = use
        self.frequency = frequency


# il is an ordered sequence of instructions
# il stands for intermediate or internal language
il: List[Instruction] = None

# register interference graph = set of edges
# each edge being specified by the set of its endpoints
graph = set()

# set of available colors (machine registers)
colors = ['red', 'blue', 'yellow', 'green']

# gives estimated cost of spilling each symbolic register
cost = {}

# set of spilled symbolic registers
spilled = set()


def run(input_il, input_colors):
    # TODO restructure so global is not necessary
    global il
    global colors

    il = input_il
    colors = input_colors

    if color_il() is None:
        estimate_spill_costs()
        decide_spills()
        insert_spill_code()
        color_il()


def run():
    if color_il() is None:
        estimate_spill_costs()
        decide_spills()
        insert_spill_code()
        return color_il()


def color_il():
    build_graph()
    coalesce_nodes()
    coloring = color_graph(graph, registers_in_il())
    if coloring is None:
        return None
    rewrite_il(coloring)
    return coloring


def build_graph():
    global graph
    graph = set()
    liveness = None

    for instruction in il:
        if instruction.opcode == 'bb':
            liveness = {}

            for dec in [dec for dec in instruction.dec if not dec.dead]:
                liveness[dec.reg] = liveness.get(dec.reg, 0) + 1

        else:
            for use in [use for use in instruction.use if use.dead]:
                liveness[use.reg] -= 1
                if liveness[use.reg] == 0:
                    liveness.pop(use.reg)
            for dec in instruction.dec:
                for key, value in liveness.items():
                    if key != dec.reg:
                        # TODO should graph have edges in both directions?
                        graph.add((dec.reg, key))
                        graph.add((key, dec.reg))
                if not dec.dead:
                    liveness[dec.reg] = liveness.get(dec.reg, 0) + 1


# TODO can I come up with a better name for this function
def copy_check(instruction: Instruction):
    if len(instruction.dec) == 0 or len(instruction.use) == 0:
        return False

    source = instruction.dec[0].reg
    target = instruction.use[0].reg

    return (instruction.opcode == 'copy' and
            source != target and
            (source, target) not in graph)


def coalesce_nodes():
    global graph

    modified = True

    while modified:
        found = next((instruction for instruction in il if copy_check(instruction)), None)
        if found is not None:
            source = found.dec[0].reg
            target = found.use[0].reg

            f = {source: target}

            graph = set([(f.get(source, source), target) for source, target in graph])
            rewrite_il(f)
        else:
            modified = False


def color_graph(g, n):
    if len(n) == 0:
        return {}

    node = next((node for node in n if len(neighbors(node, g)) < len(colors)), None)
    if node is None:
        return None

    coloring = color_graph([(x, y) for (x, y) in g if x != node and y != node],
                           [n for n in n if n != node])
    if coloring is None:
        return None

    neighbor_colors = [coloring[neighbor] for neighbor in neighbors(node, g)]
    coloring[node] = choice([color for color in colors if color not in neighbor_colors])

    return coloring


def estimate_spill_costs():
    global cost
    cost = {}

    frequency = None

    for instruction in il:
        if instruction.opcode == 'bb':
            frequency = instruction.frequency
        else:
            registers = registers_in_il()

            for reg in registers:
                cost[reg] = cost.get(reg, 0) + frequency


def decide_spills():
    global spilled
    spilled = set()

    g = graph.copy()
    n = registers_in_il()

    while len(n) != 0:
        node = next((node for node in n if len(neighbors(node, g)) < len(colors)), None)
        if node is None:
            node = next(x for x in n if cost[x] == min(cost.values()))
            spilled.add(node)

        g = [(x, y) for (x, y) in g if x != node and y != node]
        n.remove(node)


def insert_spill_code():
    global il

    newil = []

    for instruction in il:
        if instruction.opcode == 'bb':
            newil.append(
                Instruction(
                    'bb',
                    [dec for dec in instruction.dec if dec.reg not in spilled],
                    instruction.use.copy()
                )
            )
        else:
            before = []
            after = []
            newdef = []
            newuse = []

            for use in instruction.use:
                if use.reg in spilled:
                    newuse.append(Use(use.reg, True))
                    before.append(Instruction(
                        'reload',
                        [Dec(use.reg, False)],
                        []
                    ))
                else:
                    newuse.append(Use(use.reg, use.dead))
            for dec in instruction.dec:
                if dec.reg in spilled:
                    newdef.append(Dec(dec.reg, False))
                    after.append(Instruction(
                        'spill',
                        [],
                        [Use(dec.reg, True)]
                    ))
                else:
                    newdef.append(Dec(dec.reg, dec.dead))

            newil.extend(before + [Instruction(instruction.opcode, newdef, newuse)] + after)

    il = newil


def rewrite_il(f: dict):
    global il
    il = [Instruction(
        instruction.opcode,
        [Dec(f.get(dec.reg, dec.reg), dec.dead) for dec in instruction.dec],
        [Use(f.get(use.reg, use.reg), use.dead) for use in instruction.use]
    ) for instruction in il]


def registers_in_il():
    reg = set()

    for instruction in il:
        for dec in instruction.dec:
            reg.add(dec.reg)
        for use in instruction.use:
            reg.add(use.reg)

    return reg


def neighbors(x, g):
    return [target for (source, target) in g if x == source]
