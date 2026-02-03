import logging
import sys

from cpip.core import PpLexer, IncludeHandler


def main():
    print('Processing:', sys.argv[1])
    system_includes = []
    system_includes.extend(IncludeHandler.get_platform_system_include_paths('C'))
    system_includes.append('../sys')
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr', ],
        theSysDirs=system_includes,
    )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(filename)24s#%(lineno)-4d - %(levelname)-8s %(message)s',
        stream=sys.stdout,
    )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    for tok in myLex.ppTokens(minWs=True):
        print(tok)
    print(' File Include Graph '.center(75, '='))
    print(myLex.fileIncludeGraphRoot)
    print(' File Include Graph END '.center(75, '='))
    print(' Macro Environment '.center(75, '='))
    print(myLex.macroEnvironment)
    print(' Macro Environment END '.center(75, '='))


if __name__ == "__main__":
    main()
