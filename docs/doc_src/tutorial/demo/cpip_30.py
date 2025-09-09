import os
import sys

from cpip.core import FileIncludeGraph
from cpip.core import IncludeHandler
from cpip.core import PpLexer

PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


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
        r = '%s%04d %s %d\n' % (self.PAD * d, self._lineNum, self._name, self._t)
        for aC in self._children:
            r += aC.retStr(d + 1)
        return r


def main():
    include_handler = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/usr'), ],
        theSysDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/sys'), ],
    )
    lexer = PpLexer.PpLexer(sys.argv[1], include_handler)
    tu = ''.join(tok.t for tok in lexer.ppTokens(minWs=True))
    visitor = FileIncludeGraph.FigVisitorTree(MyVisitorTreeNode)
    lexer.fileIncludeGraphRoot.acceptVisitor(visitor)
    tree = visitor.tree()
    print(tree)
    return 0


if __name__ == "__main__":
    exit(main())
