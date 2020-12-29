import register_allocation
from register_allocation import Dec, Use, Instruction, IntermediateLanguage, Graph


def test_basic_example():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'b = a + 2',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'c = b * b',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        Instruction(
            'b = c + 1',
            [Dec('b', False)],
            [Use('c', True)]
        ),
        Instruction(
            'return b * a',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])
    colors = ['tab:red', 'tab:blue']

    graph, coloring = register_allocation.run(il, colors)

    assert graph is not None
    assert coloring is not None


def test_subsumption_example():
    il = IntermediateLanguage([
        Instruction(
            'bb',
            [Dec('a', False)],
            []),
        Instruction(
            'b = a + 2',
            [Dec('b', False)],
            [Use('a', False)]
        ),
        Instruction(
            'c = b * b',
            [Dec('c', False)],
            [Use('b', True)]
        ),
        # This example introduces copy. Here we copy c to d and c goes dead.
        Instruction(
            'copy',
            [Dec('d', False)],
            [Use('c', True)]
        ),
        # Instead of adding to c we add to d instead.
        Instruction(
            'b = d + 1',
            [Dec('b', False)],
            [Use('d', True)]
        ),
        Instruction(
            'return b * a',
            [],
            [Use('a', True), Use('b', True)]
        )
    ])
    colors = ['tab:red', 'tab:blue']

    graph, coloring = register_allocation.run(il, colors)

    assert graph is not None
    assert coloring is not None


def test_multiple_bb_example():
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
    colors = ['tab:red', 'tab:blue', 'tab:orange', 'tab:green']

    graph, coloring = register_allocation.run(il, colors)

    assert graph is not None
    assert coloring is not None


def test_spill_example():
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
            'd := -a',
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
            [],
            frequency=0.75
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
            frequency=0.25
        ),
        Instruction(
            'b := d + e',
            [Dec('b', False)],
            [Use('d', True), Use('e', False)]
        ),
        Instruction(
            'e := e - 1',
            [Dec('e', False)],
            [Use('e', True)]
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
    colors = ['tab:red', 'tab:blue', 'tab:green']

    graph, coloring = register_allocation.run(il, colors)

    assert graph is not None
    assert coloring is not None


def test_frequency_example():
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
            frequency=0.9
        ),
        Instruction(
            'b := d + e',
            [Dec('b', False)],
            [Use('d', True), Use('e', False)]
        ),
        Instruction(
            'e := e - 1',
            [Dec('e', False)],
            [Use('e', True)]
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
    colors = ['tab:red', 'tab:blue', 'tab:green']

    graph, coloring = register_allocation.run(il, colors)

    assert graph is not None
    assert coloring is not None
