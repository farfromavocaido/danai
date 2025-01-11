# danai/summarymaker/processing/__init__.py
"""
Processing submodule initialiser.
Provides a single place to import all processors
so they can be more easily used elsewhere.
"""

from .remover import RemoveCommentsProcessor
from .truncator import TruncateProcessor
from .typeremover import RemoveTypingHintsProcessor
from .printremover import RemovePrintStatementsProcessor
from .importcondenser import CondenseImportsProcessor


__all__ = [
    "RemoveCommentsProcessor",
    "TruncateProcessor",
    "RemoveTypingHintsProcessor",
    "RemovePrintStatementsProcessor",
    "CondenseImportsProcessor"
]
