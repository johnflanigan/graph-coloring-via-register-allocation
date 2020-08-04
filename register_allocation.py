from typing import List, Callable


class Dec:
    def __init__(self, reg: str, dead: bool):
        self.reg = reg
        self.dead = dead


class Use:
    def __init__(self, reg: str, dead: bool):
        self.reg = reg
        self.dead = dead


class Instruction:
    def __init__(self, opcode: str, dec: List[Dec], use: List[Use]):
        self.opcode = opcode
        self.dec = dec
        self.use = use


# il is an ordered sequence of instructions
# il stands for intermediate or internal language
il: List[Instruction] = None

# register interference graph = set of edges
# each edge being specified by the set of its endpoints
graph = set()

# set of available colors (machine registers)
colors = None

# gives estimated cost of spilling each symbolic register
cost = None

# set of spilled symbolic registers
spilled = None


def color_il():
    build_graph()
    coalesce_nodes()
    coloring = color_graph(graph, registers_in_il())
    if coloring is None:
        return None
    rewrite_il(coloring)
    return coloring


def build_graph():
    liveness = {}

    for instruction in il:
        if instruction.opcode == 'bb':
            for dec in [dec for dec in instruction.dec if not dec.dead]:
                if dec.reg in liveness:
                    liveness[dec.reg] += 1
                else:
                    liveness[dec.reg] = 1

        else:
            for use in [use for use in instruction.use if use.dead]:
                liveness[use.reg] -= 1
                if liveness[use.reg] == 0:
                    liveness.pop(use.reg)
            for dec in instruction.dec:
                for key, value in liveness.items():
                    if key != dec.reg:
                        graph.add((dec.reg, key))
                if not dec.dead:
                    if dec.reg in liveness:
                        liveness[dec.reg] += 1
                    else:
                        liveness[dec.reg] = 1


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

            def f(x):
                if x == source:
                    return target
                else:
                    return x

            graph = set([(f(source), target) for source, target in graph])
            rewrite_il(f)
        else:
            modified = False


def color_graph(g, n):
    pass


def estimate_spill_costs():
    pass


def decide_spills():
    pass


def insert_spill_code():
    pass


def rewrite_il(f: Callable[[str], str]):
    global il
    il = [Instruction(
        instruction.opcode,
        [Dec(f(dec.reg), dec.dead) for dec in instruction.dec],
        [Use(f(use.reg), use.dead) for use in instruction.use]
    ) for instruction in il]


def registers_in_il():
    pass


def neighbors(x, g):
    pass
