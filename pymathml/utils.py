"""A collection of functions to facilitate creation of expressions.

"""
from pymathml.core import (Identifier, Operator, Table, TableRow, TableEntry,
                           Under, )


def identifiers(*names, **attributes):
    """Return instances of Identifier with specified names.

    The **attributes are passed to the initializer of all returned
    instances of Identifier.
    """
    return tuple(Identifier(name, **attributes) for name in names)


def table(cells, **attributes):
    """Create a Table.

    The cells of the returned table are specified as an iterable of
    iterables. The **attributes are passed to the initializer of the
    Table object (attributes cannot be set for the nested TableRow and
    TableEntry objects)
    """
    return Table(*[TableRow(*[TableEntry(e) for e in r]) for r in cells],
                 **attributes)


def underbrace(expr, underscript):
    """Create an underbraced expression.

    The LaTeX equivalent is:

        \\underbrace{expr}_{underscript}
    """
    return Under(expr, Under(Operator('\N{BOTTOM CURLY BRACKET}'), underscript,
                             accentunder='true'))
