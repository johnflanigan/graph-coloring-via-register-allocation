import register_allocation
from register_allocation import Dec, Use, Instruction


def test_build_graph():
    register_allocation.il = [
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
    ]

    register_allocation.build_graph()

    assert len(register_allocation.graph) == 2
    assert ('b', 'a') in register_allocation.graph
    assert ('c', 'a') in register_allocation.graph


def test_coalesce_nodes():
    register_allocation.il = [
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
    ]

    register_allocation.graph = {('b', 'a'), ('d', 'a'), ('c', 'a')}

    register_allocation.coalesce_nodes()

    assert len(register_allocation.graph) == 2
    assert ('b', 'a') in register_allocation.graph
    assert ('c', 'a') in register_allocation.graph


def test_registers_in_il():
    register_allocation.il = [
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
    ]

    registers = register_allocation.registers_in_il()

    assert len(registers) == 4


def test_color_il():
    register_allocation.il = [
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
    ]

    coloring = register_allocation.color_il()

    assert coloring is not None
