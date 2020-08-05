import register_allocation
from register_allocation import Dec, Use, Instruction, IntermediateLanguage, Graph


def test_build_graph():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'op1',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'op2',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        Instruction(
            'op3',
            [Dec('b', False)],
            [Use('c', True)]
        ),
        Instruction(
            'ret',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])

    graph = register_allocation.build_graph(il)

    assert graph.contains_edge('a', 'b')
    assert graph.contains_edge('b', 'a')
    assert graph.contains_edge('a', 'c')
    assert graph.contains_edge('c', 'a')


def test_coalesce_nodes():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'op1',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'op2',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        Instruction(
            'copy',
            [Dec('d', False)],
            [Use('c', True)]
        ),
        Instruction(
            'op3',
            [Dec('b', False)],
            [Use('d', True)]
        ),
        Instruction(
            'ret',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])

    graph = Graph()
    graph.add_edge('b', 'a')
    graph.add_edge('d', 'a')
    graph.add_edge('c', 'a')

    register_allocation.coalesce_nodes(il, graph)

    assert graph.contains_edge('b', 'a')
    assert graph.contains_edge('c', 'a')
    assert not graph.contains_edge('d', 'a')


def test_registers_in_il():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'op1',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'op2',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        Instruction(
            'copy',
            [Dec('d', False)],
            [Use('c', True)]
        ),
        Instruction(
            'op3',
            [Dec('b', False)],
            [Use('d', True)]
        ),
        Instruction(
            'ret',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])

    registers = il.registers()

    assert len(registers) == 4


def test_color_il():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'op1',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'op2',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        Instruction(
            'op3',
            [Dec('b', False)],
            [Use('c', True)]
        ),
        Instruction(
            'ret',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])
    colors = ['red', 'blue']

    graph, coloring = register_allocation.color_il(il, colors)

    assert coloring is not None


def test_color_il_with_multiple_bb():
    # http://web.cecs.pdx.edu/~mperkows/temp/register-allocation.pdf
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('b', False), Dec('c', False), Dec('f', False)],
            []),
        Instruction(
            'a := b + c',
            [Dec('a', False)],
            [Use('b', True), Use('c', False)]
        ),
        Instruction(
            'd := a',
            [Dec('d', False)],
            [Use('a', True)]
        ),
        Instruction(
            'e := d + f',
            [Dec('e', False)],
            [Use('d', False), Use('f', False)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('e', False)],
            []),
        Instruction(
            'f := 2 + e',
            [Dec('f', False)],
            [Use('e', True)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('d', False), Dec('e', False), Dec('f', False)],
            []),
        Instruction(
            'b := d + e',
            [Dec('b', False)],
            [Use('d', True), Use('e', False)]
        ),
        Instruction(
            'e := e - 1',
            [Dec('e', False)],
            [Use('e', False)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('f', False)],
            []),
        Instruction(
            'b := f + c',
            [Dec('b', True)],
            [Use('c', False), Use('f', False)]
        ),
    ])
    colors = ['red', 'blue', 'yellow', 'green']

    graph, coloring = register_allocation.run(il, colors)

    assert coloring is not None


def test_color_il_with_spills():
    # http://web.cecs.pdx.edu/~mperkows/temp/register-allocation.pdf
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('b', False), Dec('c', False), Dec('f', False)],
            []),
        Instruction(
            'a := b + c',
            [Dec('a', False)],
            [Use('b', True), Use('c', False)]
        ),
        Instruction(
            'd := a',
            [Dec('d', False)],
            [Use('a', True)]
        ),
        Instruction(
            'e := d + f',
            [Dec('e', False)],
            [Use('d', False), Use('f', False)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('e', False)],
            []),
        Instruction(
            'f := 2 + e',
            [Dec('f', False)],
            [Use('e', True)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('d', False), Dec('e', False), Dec('f', False)],
            []),
        Instruction(
            'b := d + e',
            [Dec('b', False)],
            [Use('d', True), Use('e', False)]
        ),
        Instruction(
            'e := e - 1',
            [Dec('e', False)],
            [Use('e', False)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('f', False)],
            []),
        Instruction(
            'b := f + c',
            [Dec('b', True)],
            [Use('c', False), Use('f', False)]
        ),
    ])
    colors = ['red', 'blue', 'yellow']

    graph, coloring = register_allocation.run(il, colors)

    assert coloring is not None


def test_color_il_with_spills_and_frequency():
    # http://web.cecs.pdx.edu/~mperkows/temp/register-allocation.pdf
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('b', False), Dec('c', False), Dec('f', False)],
            [],
            frequency=1
        ),
        Instruction(
            'a := b + c',
            [Dec('a', False)],
            [Use('b', True), Use('c', False)]
        ),
        Instruction(
            'd := a',
            [Dec('d', False)],
            [Use('a', True)]
        ),
        Instruction(
            'e := d + f',
            [Dec('e', False)],
            [Use('d', False), Use('f', False)]
        ),

        # Using negative frequency to force f to be spilled
        Instruction(
            'bb',
            [Dec('c', False), Dec('e', False)],
            [],
            frequency=-0.1
        ),
        Instruction(
            'f := 2 + e',
            [Dec('f', False)],
            [Use('e', True)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('d', False), Dec('e', False), Dec('f', False)],
            [],
            frequency=1
        ),
        Instruction(
            'b := d + e',
            [Dec('b', False)],
            [Use('d', True), Use('e', False)]
        ),
        Instruction(
            'e := e - 1',
            [Dec('e', False)],
            [Use('e', False)]
        ),

        Instruction(
            'bb',
            [Dec('c', False), Dec('f', False)],
            [],
            frequency=1
        ),
        Instruction(
            'b := f + c',
            [Dec('b', True)],
            [Use('c', False), Use('f', False)]
        ),
    ])
    colors = ['lightcoral', 'lightblue', 'lightgreen']

    graph, coloring = register_allocation.run(il, colors)

    assert coloring is not None
