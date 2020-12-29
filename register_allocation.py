import copy
from random import choice
from typing import List, Set, Collection, Dict, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx


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


class IntermediateLanguage:
    """
    The intermediate language. Maintains an ordered sequence of instructions.
    """

    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions

    def overwrite_il(self, new_instructions: List[Instruction]):
        self.instructions = new_instructions

    def rewrite_il(self, f: Dict) -> None:
        self.instructions = [Instruction(
            instruction.opcode,
            [Dec(f.get(dec.reg, dec.reg), dec.dead) for dec in instruction.dec],
            [Use(f.get(use.reg, use.reg), use.dead) for use in instruction.use]
        ) for instruction in self.instructions]

    def registers(self) -> Set[str]:
        reg = set()

        for instruction in self.instructions:
            for dec in instruction.dec:
                reg.add(dec.reg)
            for use in instruction.use:
                reg.add(use.reg)

        return reg


class Graph:
    """
    The register interference graph.
    """

    def __init__(self):
        self._adjacency_list = {}

    def __copy__(self):
        cls = self.__class__
        new_graph = self.__new__(cls)
        new_graph._adjacency_list = copy.deepcopy(self._adjacency_list)
        return new_graph

    def add_edge(self, x, y):
        """
        Add an edge to the graph.

        The interference graph is undirected so add_edge('a', 'b') and add_edge('b', 'a') have the same effect.
        """
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
        return y in self._adjacency_list.get(x, [])

    def remove_node(self, node):
        if node in self._adjacency_list:
            self._adjacency_list.pop(node)
        for key in self._adjacency_list.keys():
            if node in self._adjacency_list.get(key):
                self._adjacency_list.get(key).remove(node)

    def rename_node(self, from_label, to_label):
        from_list = self._adjacency_list.pop(from_label, [])
        to_list = self._adjacency_list.get(to_label, [])
        self._adjacency_list[to_label] = list(set(from_list + to_list))

        for key in self._adjacency_list.keys():
            self._adjacency_list[key] = list(set(
                [to_label if value == from_label else value for value in self._adjacency_list[key]]
            ))

    def neighbors(self, x):
        return self._adjacency_list.get(x, [])

    def plot(self, coloring, title):
        G = nx.Graph()

        # Sorting to get repeatable graphs
        nodes = sorted(self._adjacency_list.keys())
        ordered_coloring = [coloring.get(node, 'grey') for node in nodes]
        G.add_nodes_from(nodes)

        for key in self._adjacency_list.keys():
            for value in self._adjacency_list[key]:
                G.add_edge(key, value)

        plt.title(title)
        nx.draw(G, pos=nx.circular_layout(G), node_color=ordered_coloring, with_labels=True, font_weight='bold')
        plt.show()


def run(il: IntermediateLanguage, colors: List[str]) -> Tuple[Optional[Graph], Optional[Dict[str, str]]]:
    graph, coloring = color_il(il, colors)
    if coloring is None:
        graph.plot({}, 'Initial')
        cost = estimate_spill_costs(il)
        spilled = decide_spills(il, graph, colors, cost)
        insert_spill_code(il, spilled)
        graph, coloring = color_il(il, colors)
        graph.plot({}, 'After Spilling')
        graph.plot(coloring, 'Colored')

    return graph, coloring


def color_il(il: IntermediateLanguage, colors: List[str]) -> Tuple[Optional[Graph], Optional[Dict[str, str]]]:
    graph = build_graph(il)
    graph.plot({}, 'Initial')
    coalesce_nodes(il, graph)
    # graph.plot({}, 'After Coalescing')
    coloring = color_graph(graph, il.registers(), colors)

    if coloring is None:
        return graph, None

    # graph.plot(coloring, 'Colored')
    return graph, coloring


def build_graph(il: IntermediateLanguage) -> Graph:
    graph = Graph()
    liveness = None

    for instruction in il.instructions:
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

    return graph


def is_unnecessary_copy(instruction: Instruction, graph: Graph) -> bool:
    if len(instruction.dec) == 0 or len(instruction.use) == 0:
        return False

    source = instruction.dec[0].reg
    target = instruction.use[0].reg

    return (instruction.opcode == 'copy' and
            source != target and
            not graph.contains_edge(source, target))


def coalesce_nodes(il: IntermediateLanguage, graph: Graph) -> None:
    modified = True

    while modified:
        found = next((instruction for instruction in il.instructions if is_unnecessary_copy(instruction, graph)), None)
        if found is not None:
            source = found.dec[0].reg
            target = found.use[0].reg

            f = {source: target}

            graph.rename_node(source, target)
            il.rewrite_il(f)
        else:
            modified = False


def color_graph(g: Graph, n: Collection[str], colors: List[str]) -> Optional[Dict[str, str]]:
    if len(n) == 0:
        return {}

    node = next((node for node in n if len(g.neighbors(node)) < len(colors)), None)
    if node is None:
        return None

    g_copy = copy.copy(g)
    g_copy.remove_node(node)
    coloring = color_graph(g_copy, [n for n in n if n != node], colors)
    if coloring is None:
        return None

    neighbor_colors = [coloring[neighbor] for neighbor in g.neighbors(node)]
    coloring[node] = choice([color for color in colors if color not in neighbor_colors])

    return coloring


def estimate_spill_costs(il: IntermediateLanguage) -> Dict[str, float]:
    """
    :param il: The intermediate language to compute spill costs on.
    :return: The estimated cost of spilling each symbolic register
    """
    cost = {}

    frequency = None

    for instruction in il.instructions:
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

    return cost


def decide_spills(il: IntermediateLanguage, graph: Graph, colors: List[str], cost: Dict[str, float]) -> Set[str]:
    """
    Determines which symbolic registers to spill.

    :param il: The intermediate language
    :param graph: The interference graph
    :param colors: Possible colors
    :param cost: Estimated cost of spilling each symbolic register
    :return: The set of spilled symbolic registers
    """
    spilled = set()

    g = copy.copy(graph)
    n = il.registers()

    while len(n) != 0:
        node = next((node for node in n if len(g.neighbors(node)) < len(colors)), None)
        if node is None:
            node = next(x for x in n if cost[x] == min([cost[y] for y in n]))
            spilled.add(node)

        g.remove_node(node)
        n.remove(node)

    return spilled


def insert_spill_code(il: IntermediateLanguage, spilled: Set[str]) -> None:
    new_il = []

    for instruction in il.instructions:
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

    il.overwrite_il(new_il)
