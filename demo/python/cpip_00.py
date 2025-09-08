import logging
import sys
from cpip.core import PpLexer, IncludeHandler

# TODO: Get system includes
# TODO: Aline the documentation in PpLexer tutorial to this code.

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr',],
        theSysDirs=['../sys',],
        )

    logging.basicConfig(
        level=10,
        format='%(asctime)s - %(filename)24s#%(lineno)-4d - %(levelname)-8s %(message)s',
        stream=sys.stdout,
    )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    for tok in myLex.ppTokens(minWs=True):
        print(tok)
#        print(tok.t, end=' ')
#        print(myLex.condState)
#        print(myLex.fileStack)
#        print(myLex.fileLineCol)
#         print(myLex.macroEnvironment)
    print(' File Include Graph '.center(75, '='))
    print(myLex.fileIncludeGraphRoot)
    print(' File Include Graph END '.center(75, '='))
    print(' Macro Environment '.center(75, '='))
    print(myLex.macroEnvironment)
    print(' Macro Environment END '.center(75, '='))

if __name__ == "__main__":
    main()
