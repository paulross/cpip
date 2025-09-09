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
    for _tok in lexer.ppTokens(condLevel=2):
        # For clarity, we just print out the basename of the files.
        print(
            f'{os.path.basename(lexer.fileName):10}'
            f' {lexer.lineNum:4d} {lexer.colNum:2d}'
            f' {lexer.condState}'
        )
    return 0


if __name__ == "__main__":
    exit(main())
