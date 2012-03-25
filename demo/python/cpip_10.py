import sys
from cpip.core import PpLexer
from cpip.core import IncludeHandler
from cpip.core import FileIncludeGraph

class MyVisitorTreeNode(FileIncludeGraph.FigVisitorTreeNodeBase):
    PAD = '  '
    def __init__(self, theFig, theLineNum):
        super(MyVisitorTreeNode, self).__init__(theLineNum)
        if theFig is None:
            self._name = None
            self._t = 0
        else:
            self._name = theFig.fileName
            self._t = theFig.numTokens
            
    def finalise(self):
        # Tot up tokens
        for aChild in self._children:
            aChild.finalise()
            self._t += aChild._t
            
    def __str__(self):
        return self.retStr(0)
        
    def retStr(self, d):
        r = '%s%04d %s %d\n' % (self.PAD*d, self._lineNum, self._name, self._t)
        for aC in self._children:
            r += aC.retStr(d+1)
        return r

def main():
    print('Processing:', sys.argv[1])
    myH = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=['../usr',],
        theSysDirs=['../sys',],
        )
    myLex = PpLexer.PpLexer(sys.argv[1], myH)
    tu = ''.join(tok.t for tok in myLex.ppTokens(minWs=True))
    myVis = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
    myLex.fileIncludeGraphRoot.acceptVisitor(myVis)
    myTree = myVis.tree()
    print(myTree)

if __name__ == "__main__":
    main()
