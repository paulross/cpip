import sys
from cpip.core import PpLexer, IncludeHandler

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr',],
        theSysDirs=['../sys',],
        )

    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    for tok in myLex.ppTokens(minWs=True):
#        print(tok.t, end=' ')
#        print(myLex.condState)
#        print(myLex.fileStack)
#        print(myLex.fileLineCol)
        print(myLex.macroEnvironment)
    print(' File Include Graph '.center(75, '='))
    print(myLex.fileIncludeGraphRoot)
    print(' File Include Graph END '.center(75, '='))
    print(' Macro Environment '.center(75, '='))
    print(myLex.macroEnvironment)
    print(' Macro Environment END '.center(75, '='))

if __name__ == "__main__":
    main()
