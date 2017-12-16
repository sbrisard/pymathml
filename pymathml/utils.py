"""A collection of functions to facilitate creation of expressions.

"""

def table(rows, **attributes):
    return Table(*[TableRow(*[TableEntry(e) for e in r]) for r in rows],
                 **attributes)
