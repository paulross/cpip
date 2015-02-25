import sys
from cpip.core import PpLexer
from cpip.core import IncludeHandler

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr',],
        theSysDirs=['../sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    tu = ''.join(tok.t for tok in myLex.ppTokens(minWs=True))
    print(repr(myLex.fileIncludeGraphRoot))

if __name__ == "__main__":
    main()
