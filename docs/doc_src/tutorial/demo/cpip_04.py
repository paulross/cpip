import sys
from cpip.core import PpLexer, IncludeHandler

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['proj/usr',],
        theSysDirs=['proj/sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    for tok in myLex.ppTokens(minWs=True):
        print(tok.t, end=' ')

if __name__ == "__main__":
    main()
