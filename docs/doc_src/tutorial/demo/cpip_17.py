import os
import sys

from cpip.core import IncludeHandler
from cpip.core import PpLexer

PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


def main() -> int:
    print('Processing:', sys.argv[1])
    include_handler = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/usr'), ],
        theSysDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/sys'), ],
    )
    lexer = PpLexer.PpLexer(sys.argv[1], include_handler)
    tu = ''.join(tok.t for tok in lexer.ppTokens(minWs=True))

    print()
    print(' Translation Unit '.center(75, '='))
    print(tu)
    print(' Translation Unit END '.center(75, '='))

    print()
    print(' File Include Graph '.center(75, '='))
    print(lexer.fileIncludeGraphRoot)
    print(' File Include Graph END '.center(75, '='))

    print()
    print(' Conditional Compilation Graph '.center(75, '='))
    print(lexer.condCompGraph)
    print(' Conditional Compilation Graph END '.center(75, '='))

    print()
    print(' Macro Environment '.center(75, '='))
    print(lexer.macroEnvironment)
    print(' Macro Environment END '.center(75, '='))

    print()
    print(' Macro History '.center(75, '='))
    print(lexer.macroEnvironment.macroHistory(incEnv=False, onlyRef=False))
    print(' Macro History END '.center(75, '='))

    return 0


if __name__ == "__main__":
    exit(main())
