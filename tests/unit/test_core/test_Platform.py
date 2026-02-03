import pytest

from cpip.core import Platform


@pytest.mark.parametrize(
    'input_line, expected',
    (
        (
            "note: use 'iso9899:199409' for 'ISO C 1990 with amendment 1' standard",
            ("'iso9899:199409'", 'ISO C 1990 with amendment 1'),
        ),
        (
            "note: use 'gnu89' or 'gnu90' for 'ISO C 1990 with GNU extensions' standard",
            ("'gnu89' or 'gnu90'", 'ISO C 1990 with GNU extensions'),
        ),
        (
            "note: use 'c89', 'c90', or 'iso9899:1990' for 'ISO C 1990' standard",
            ("'c89', 'c90', or 'iso9899:1990'", 'ISO C 1990'),
        ),
    )
)
def test_platform_RE_STANDARDS_LINE(input_line, expected):
    m = Platform.PlatformConfig.RE_STANDARDS_LINE.match(input_line)
    assert m is not None
    assert len(m.groups()) == 2
    assert m.groups() == expected


@pytest.mark.parametrize(
    'input_line, expected_stds, expected_description',
    (
        (
            "note: use 'iso9899:199409' for 'ISO C 1990 with amendment 1' standard",
            ['iso9899:199409',],
            'ISO C 1990 with amendment 1',
        ),
        (
            "note: use 'gnu89' or 'gnu90' for 'ISO C 1990 with GNU extensions' standard",
            ["gnu89", "gnu90"],
            'ISO C 1990 with GNU extensions',
        ),
        (
            "note: use 'c89', 'c90', or 'iso9899:1990' for 'ISO C 1990' standard",
            ["c89", "c90", 'iso9899:1990'],
            'ISO C 1990',
        ),
    )
)
def test_platform_RE_STANDARDS_LINE_split_logic(input_line, expected_stds, expected_description):
    m = Platform.PlatformConfig.RE_STANDARDS_LINE.match(input_line)
    assert m is not None
    assert len(m.groups()) == 2
    assert m.group(1).startswith("'")
    assert m.group(1).endswith("'")
    stds_str = m.group(1)
    stds_str = stds_str.replace(', or', ' or')
    stds_str = stds_str.replace(',', ' or')
    stds = stds_str.split(' or ')
    # print()
    # print(m.groups())
    # print(stds_str)
    # print(stds)
    my_stds = []
    for std in stds:
        assert std.startswith("'")
        assert std.endswith("'")
        my_stds.append(std[1:-1])
    assert my_stds == expected_stds
    assert m.group(2) == expected_description
