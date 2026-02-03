"""This provides a configuration class that encapsulates all the classes the PpLexer or a preprocessor needs.

includeHandler,
diagnostic=None,
pragmaHandler=None,
autoDefineDateTime=True,
gccExtensions=False,

Cpp.predefinedFileObjects
preIncFiles=None,
stdPredefMacros=None,

PpLexer needs this as it is output control.
annotateLineFile=False,

"""
import dataclasses

from cpip.core import Standards
from cpip.core import IncludeHandler
from cpip.core import CppDiagnostic
from cpip.core import PragmaHandler


@dataclasses.dataclass
class PpConfiguration:
    standards: Standards
    includeHandler: IncludeHandler
    pragmaHandler: PragmaHandler
    cppDiagnostic: CppDiagnostic
    autoDefineDateTime: bool
    embedIncludeHandler: IncludeHandler
