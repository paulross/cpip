import pytest

from cpip.core import Standards


def test_generic_standards():
    assert Standards.Standards.GENERIC_STANDARDS == ['K&R', 'ANSI', 'C90', 'C95', 'C99', 'C11', 'C17/C18', 'C23']


def test_generic_standard_argument():
    assert set(Standards.Standards.GENERIC_STANDARD_ARGUMENT.keys()) == set(Standards.Standards.GENERIC_STANDARDS)


@pytest.mark.parametrize(
    'standard, expected',
    (
        ('k&r', "<class 'cpip.core.Standards.Standards'>: Std: k&r GNU: False"),
        ('ansi', "<class 'cpip.core.Standards.Standards'>: Std: ansi GNU: False"),
    )
)
def test_ctor(standard, expected):
    std = Standards.Standards(standard, False)
    assert str(std) == expected


@pytest.mark.parametrize(
    'standard, expected',
    (
        ('k&r', False),
        ('ansi', False),
        ('c90', True),
        ('c95', True),
        ('c99', True),
        ('c11', True),
        ('c17', True),
        ('c18', True),
        ('c23', True),
    )
)
def test_has_digraphs(standard, expected):
    std = Standards.Standards(standard, False)
    assert std.has_digraphs() == expected


def test_help_text():
    help_text = Standards.Standards.help_text()
    print()
    for line in help_text:
        print(line)
    assert help_text == [
        'K&R (The C Programming Language, Kernighan and Ritchie, First Edition, ISBN 9780131101630) --std=k&r.',
        'ANSI (ANSI X3.159-1989) --std=ansi, --std=c89.',
        'C90 (ISO/IEC 9899:1990) --std=c90, --std=iso9899:1990, --std=iso9899:199409.',
        'C95 (ISO/IEC 9899-1:1994, ISO/IEC 9899:1990/AMD1:1995) --std=c95.',
        'C99 (ISO/IEC 9899:1999) --std=c99, --std=c9x, --std=iso9899:1999, --std=iso9899:199x.',
        'C11 (ISO/IEC 9899:2011) --std=c11, --std=c1x, --std=iso9899:2011.',
        'C17/C18 (ISO/IEC 9899:2018) --std=c17, --std=c18, --std=iso9899:2017, --std=iso9899:2018.',
        'C23 (ISO/IEC 9899:2024) --std=c23, --std=c2x, --std=iso9899:2024.'
    ]
