import os
import sys

from cpip.core import IncludeHandler
from cpip.core import PpLexer

PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


def main() -> int:
    print('Processing:', sys.argv[1])
    include_handler = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/usr'), ],
        theSysDirs=(
            IncludeHandler.get_platform_system_include_paths('C')
            + [os.path.join(PROJECT_DIRECTORY, 'proj/sys'), ]
        ),
    )
    #  We need to add the equivalent of -D __GNUC__=4 -D __x86_64__
    predefined_macros = {
        '__GNUC__': '4\n',
        '__x86_64__': '\n',
    }
    lexer = PpLexer.PpLexer(sys.argv[1], include_handler, stdPredefMacros=predefined_macros)
    for tok in lexer.ppTokens(minWs=True):
        print(tok.t, end='')
    return 0


if __name__ == "__main__":
    exit(main())
