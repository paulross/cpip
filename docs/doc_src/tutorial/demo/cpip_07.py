import sys
from cpip.core import PpLexer, IncludeHandler

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['proj/usr',],
        theSysDirs=['proj/sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    tu = ''.join(tok.t for tok in myLex.ppTokens(minWs=True))
    
    print()
    print(' Translation Unit '.center(75, '='))
    print(tu)
    print(' Translation Unit END '.center(75, '='))
    
    print()
    print(' File Include Graph '.center(75, '='))
    print(myLex.fileIncludeGraphRoot)
    print(' File Include Graph END '.center(75, '='))
    
    print()
    print(' Conditional Compilation Graph '.center(75, '='))
    print(myLex.condCompGraph)
    print(' Conditional Compilation Graph END '.center(75, '='))
    
    print()
    print(' Macro Environment '.center(75, '='))
    print(myLex.macroEnvironment)
    print(' Macro Environment END '.center(75, '='))
    
    print()
    print(' Macro History '.center(75, '='))
    print(myLex.macroEnvironment.macroHistory(incEnv=False, onlyRef=False))
    print(' Macro History END '.center(75, '='))

if __name__ == "__main__":
    main()
