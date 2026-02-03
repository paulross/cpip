import os
import sys

from cpip.core import FileIncludeGraph
from cpip.core import IncludeHandler
from cpip.core import PpLexer

PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


class Visitor(FileIncludeGraph.FigVisitorBase):

    def visitGraph(self, theFigNode, theDepth, theLine):
        # For clarity, we just print out the basename of the files.
        print(os.path.basename(theFigNode.fileName), theFigNode.findLogic)


def main() -> int:
    print('Processing:', sys.argv[1])
    include_handler = IncludeHandler.CppIncludeStdOs(
        theUsrDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/usr'), ],
        theSysDirs=[os.path.join(PROJECT_DIRECTORY, 'proj/sys'), ],
    )
    lexer = PpLexer.PpLexer(sys.argv[1], include_handler)
    tu = ''.join(tok.t for tok in lexer.ppTokens(minWs=True))
    myVis = Visitor()
    lexer.fileIncludeGraphRoot.acceptVisitor(myVis)
    return 0


if __name__ == "__main__":
    exit(main())
