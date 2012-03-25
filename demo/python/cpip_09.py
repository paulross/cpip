import sys
from cpip.core import PpLexer
from cpip.core import IncludeHandler
from cpip.core import FileIncludeGraph

class Visitor(FileIncludeGraph.FigVisitorBase):
    
    def visitGraph(self, theFigNode, theDepth, theLine):
        print(theFigNode.fileName, theFigNode.findLogic)

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr',],
        theSysDirs=['../sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    tu = ''.join(tok.t for tok in myLex.ppTokens(minWs=True))
    myVis = Visitor()
    myLex.fileIncludeGraphRoot.acceptVisitor(myVis)

if __name__ == "__main__":
    main()
