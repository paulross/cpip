import sys
from cpip.core import PpLexer, IncludeHandler

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['proj/usr',],
        theSysDirs=['proj/sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    for tok in myLex.ppTokens():
        print(tok)

if __name__ == "__main__":
    main()