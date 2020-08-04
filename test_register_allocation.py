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

    assert len(register_allocation.graph) == 4
    assert ('a', 'b') in register_allocation.graph
    assert ('b', 'a') in register_allocation.graph
    assert ('a', 'c') in register_allocation.graph
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


def test_color_il_with_multiple_bb():
    # http://web.cecs.pdx.edu/~mperkows/temp/register-allocation.pdf
    register_allocation.il = [
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
    ]

    coloring = register_allocation.color_il()

    assert coloring is not None
