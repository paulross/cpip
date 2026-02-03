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
    lexer = PpLexer.PpLexer(
        sys.argv[1],
        include_handler,
        stdPredefMacros=predefined_macros,
    )
    for _tok in lexer.ppTokens():
        # For clarity, we just print out the basename of the files.
        file_stack = [os.path.basename(f) for f in lexer.fileStack]
        file_name = os.path.basename(lexer.fileName)
        print(f'{file_name:10} {lexer.lineNum:4d} {lexer.colNum:2d} {file_stack}')
    return 0


if __name__ == "__main__":
    exit(main())
