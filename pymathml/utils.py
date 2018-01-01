"""A collection of functions to facilitate creation of expressions.

"""
from pymathml.core import Operator, Table, TableRow, TableEntry, Under


def table(rows, **attributes):
    return Table(*[TableRow(*[TableEntry(e) for e in r]) for r in rows],
                 **attributes)


def underbrace(expr, underscript):
    return Under(expr, Under(Operator('\N{BOTTOM CURLY BRACKET}'), underscript,
                             accentunder='true'))
