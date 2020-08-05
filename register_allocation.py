import copy
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


class Graph:

    def __init__(self):
        self._adjacency_list = {}

    def __copy__(self):
        cls = self.__class__
        new_graph = self.__new__(cls)
        new_graph._adjacency_list = copy.deepcopy(self._adjacency_list)
        return new_graph

    def add_edge(self, x, y):
        # Add y to x
        x_list = self._adjacency_list.get(x, [])
        if y not in x_list:
            x_list.append(y)
        self._adjacency_list[x] = x_list

        # Add x to y
        y_list = self._adjacency_list.get(y, [])
        if x not in y_list:
            y_list.append(x)
        self._adjacency_list[y] = y_list

    def contains_edge(self, x, y):
        return y in self._adjacency_list[x]

    def remove_node(self, node):
        if node in self._adjacency_list:
            self._adjacency_list.pop(node)
        for key in self._adjacency_list.keys():
            if node in self._adjacency_list.get(key):
                self._adjacency_list.get(key).remove(node)

    def rename_node(self, from_label, to_label):
        from_list = self._adjacency_list.pop(from_label, [])
        to_list = self._adjacency_list.get(to_label, [])
        self._adjacency_list[to_label] = from_list + to_list

    def neighbors(self, x):
        return self._adjacency_list.get(x, [])


# il is an ordered sequence of instructions
# il stands for intermediate or internal language
il: List[Instruction] = None

# register interference graph = set of edges
# each edge being specified by the set of its endpoints
graph = Graph()

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
    graph = Graph()
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
                        graph.add_edge(dec.reg, key)
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
            not graph.contains_edge(source, target))


def coalesce_nodes():
    global graph

    modified = True

    while modified:
        found = next((instruction for instruction in il if copy_check(instruction)), None)
        if found is not None:
            source = found.dec[0].reg
            target = found.use[0].reg

            f = {source: target}

            graph.rename_node(source, target)
            # graph = set([(f.get(source, source), target) for source, target in graph])
            rewrite_il(f)
        else:
            modified = False


def color_graph(g, n):
    if len(n) == 0:
        return {}

    node = next((node for node in n if len(g.neighbors(node)) < len(colors)), None)
    if node is None:
        return None

    g_copy = copy.copy(g)
    g_copy.remove_node(node)
    coloring = color_graph(g_copy, [n for n in n if n != node])
    if coloring is None:
        return None

    neighbor_colors = [coloring[neighbor] for neighbor in g.neighbors(node)]
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
            registers = set()

            for dec in instruction.dec:
                registers.add(dec.reg)
            for use in instruction.use:
                registers.add(use.reg)

            for reg in registers:
                cost[reg] = cost.get(reg, 0) + frequency


def decide_spills():
    global spilled
    spilled = set()

    g = copy.copy(graph)
    n = registers_in_il()

    while len(n) != 0:
        node = next((node for node in n if len(g.neighbors(node)) < len(colors)), None)
        if node is None:
            node = next(x for x in n if cost[x] == min(cost.values()))
            spilled.add(node)

        g.remove_node(node)
        n.remove(node)


def insert_spill_code():
    global il

    new_il = []

    for instruction in il:
        if instruction.opcode == 'bb':
            new_il.append(
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

            new_il.extend(before + [Instruction(instruction.opcode, newdef, newuse)] + after)

    il = new_il


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
