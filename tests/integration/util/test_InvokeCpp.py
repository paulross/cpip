import pytest

from cpip.util import InvokeCpp


@pytest.mark.parametrize(
    'stdin, filter_output, expected',
    (
        (b'', True, []),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            True,
            [
                'SPAM', 'EGGS', 'SPAM',
            ],
        ),
        (
            b'\n'.join(
                [
                    b'#define SPAM EGGS',
                    b'#define EGGS SPAM',
                    b'#define CHIPS SPAM',
                    b'SPAM',
                    b'EGGS',
                    b'CHIPS',
                ]
            ),
            False,
            [
                '# 1 "<stdin>"',
                '# 1 "<built-in>" 1',
                '# 1 "<built-in>" 3',
                '# 384 "<built-in>" 3',
                '# 1 "<command line>" 1',
                '# 1 "<built-in>" 2',
                '# 1 "<stdin>" 2',
                '',
                '',
                '',
                'SPAM',
                'EGGS',
                'SPAM',
            ],
        ),
    )
)
def test_capture_cpp_stdin_output(stdin, filter_output, expected):
    result = InvokeCpp.capture_cpp_stdin_output(stdin, filter_output)
    assert result == expected
