import sys
import hashlib
from cpip.core import PpLexer, IncludeHandler
from cpip import ExceptionCpip

def main():
    try:
        print 'Processing:', sys.argv[1]
        myH = IncludeHandler.CppIncludeStdOs(
            theUsrDirs=['../usr',],
            theSysDirs=['../sys',],
            )
        myLex = PpLexer.PpLexer(sys.argv[1], myH)
        m = hashlib.md5()
        for tok in myLex.ppTokens(minWs=True, incCond=False):
            m.update(tok.t)
            #print tok
            #print tok.t,
            #print myLex.condState
            #print 'Bad File: %s, line %d, col %d' % (myLex.fileName, myLex.lineNum, myLex.colNum) 
            #print myLex.fileStack
        #print
        #print myLex.fileIncludeGraphRoot
        #print
        #print myLex.definedMacros
        print
        print myLex.macroEnvironment.macroHistory(onlyRef=False)
        print
        print 'Checksum is: %s' % m.hexdigest()
        print
        print myLex._tokCountStk
    except ExceptionCpip, err:
        print 'Ooops: %s' % err


if __name__ == "__main__":
    main()

