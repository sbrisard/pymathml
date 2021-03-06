import numbers
import xml.etree.ElementTree as ET


class BaseExpression:
    """Base class for MathML expressions.

    This class does not provide an initializer and should *not* be
    instantiated directly. Use derived classes instead.
    """

    def __str__(self):
        return ET.tostring(self.tomathml(), encoding="unicode")

    def __add__(self, other):
        return Plus(self, other)

    def __radd__(self, other):
        return Plus(other, self)

    def __sub__(self, other):
        return Minus(self, other)

    def __rsub__(self, other):
        return Minus(other, self)

    def __mul__(self, other):
        return InvisibleTimes(self, other)

    def __rmul__(self, other):
        return InvisibleTimes(other, self)

    def __matmul__(self, other):
        return Dot(self, other)

    def __rmatmul__(self, other):
        return Dot(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __floordiv__(self, other):
        return Frac(self, other)

    def __rfloordiv__(self, other):
        return Frac(other, self)

    def __pow__(self, other):
        return Sup(self, other)

    def __neg__(self):
        return Neg(self)

    def __pos__(self):
        return Pos(self)

    def __getitem__(self, key):
        subscript = Row(*key) if isinstance(key, tuple) else key
        return Sub(self, subscript)

    def __call__(self, *args):
        return Row(self, Operator("\N{FUNCTION APPLICATION}"), Fenced(*args))

    def tomathml(self):
        """Convert this object to MathML.

        The MathML representation of this object is returned as a
        xml.etree.ElementTree.Element.
        """
        raise NotImplementedError(
            "sub-classes of BaseExpression should" " implement this method"
        )

    def _repr_html_(self):
        return ET.tostring(tomathml(self, display=("block")), encoding="unicode")


class Token(BaseExpression):
    """Token elements (see MathML specifications, section 3.1.9.1).

    This class should *not* be instanciated directly. Use derived
    classes instead (see list in documentation).
    """

    def __init__(self, value, **attributes):
        """Initialize token element."""
        self.value = value
        self.attributes = attributes

    def __repr__(self):
        params = [repr(self.value)]
        if self.attributes:
            params += ["{}='{}'".format(k, v) for k, v in self.attributes.items()]
        return "{}({})".format(self.__class__.__name__, ", ".join(params))

    def tomathml(self):
        element = ET.Element(self.tag, **self.attributes)
        element.text = str(self.value)
        return element


class Expression(BaseExpression):
    """Base class for non-token elements.

    This class is the base class for the following element types:

      - general layout schemata,
      - script and limit schemata,
      - tables and matrices.

    This class should *not* be instanciated directly. Use derived
    classes instead (see list in documentation).
    """

    def __init__(self, *expressions, **attributes):
        """Initialize expression.

        *expressions are the children of the resulting MathML
        element. They are automatically converted to Expression using
        the function expression.
        """
        self.children = [expression(e) for e in expressions]
        self.attributes = attributes

    def __repr__(self):
        params = [repr(child) for child in self.children]
        if self.attributes:
            params += ["{}='{}'".format(k, v) for k, v in self.attributes.items()]
        return "{}({})".format(self.__class__.__name__, ", ".join(params))

    def tomathml(self):
        element = ET.Element(self.tag, **self.attributes)
        for child in self.children:
            if child:
                element.append(child.tomathml())
        return element


class UnaryOperation(Expression):
    """PyMathML representation of unary operations.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """

    def tomathml(self):
        return Row(self.operator, self.children[0], **self.attributes).tomathml()


class BinaryOperation(Expression):
    """PyMathML representation of a binary operation.

    Assuming associativity, the binary operator can be applied to more
    than two operands. They are enclosed in a mrow element.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """

    def tomathml(self):
        children = [self.children[0]]
        for child in self.children[1:]:
            children.append(self.operator)
            children.append(child)
        return Row(*children, **self.attributes).tomathml()


class NaryOperation(Expression):
    """PyMathML representation of a n-ary operation.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """

    def tomathml(self):
        expr, start, end = self.children
        operator = self.operator
        if end is None:
            if start:
                operator = Under(self.operator, start)
        else:
            if start is None:
                operator = Over(self.operator, end)
            else:
                operator = UnderOver(self.operator, start, end)
        return Row(operator, expr, **self.attributes).tomathml()


#
# Automatic creation of derived classes
# =====================================
#
TOKEN_DOCSTRING = """PyMathML representation of the {1} token element.

    See MathML specifications, section {2}.

    Usage: {0}(value, **attributes)

    which produces the following MathML code:x

        <{1}>str(value)</{1}>

    (note the call to str).
    """


def token_type(name, tag, section):
    """Return a class derived from Token.

    The returned class is named name. The docstring refers to the
    specified section of the MathML specifications.
    """
    return type(
        name,
        (Token,),
        {"tag": tag, "__doc__": TOKEN_DOCSTRING.format(name, tag, section)},
    )


EXPRESSION_DOCSTRING = """PyMathML representation of the {1} element.

    See MathML specifications, section {2}.

    Usage: {0}({3}, **attributes)

    which produces the following MathML code:

        <{1}>
            {4}
        </{1}>
    """


def expression_type(name, tag, section, params=None):
    """Return a class derived from Expression.

    The returned class is named name. The docstring refers to the
    specified section of the MathML specifications. The "usage" section
    of the docstring lists the params of the initializer (*expressions
    if not specified).
    """
    placeholder = "{4}"
    doc = EXPRESSION_DOCSTRING
    if params is None:
        params_list = ["tomathml(expressions[0])", "tomathml(expressions[1])", "..."]
    else:
        params_list = ["tomathml({})".format(s.strip()) for s in params.split(",")]
    n = len(params_list)
    lines = doc.splitlines()
    for i, s in enumerate(lines):
        if placeholder in s:
            break
    lines = (
        lines[:i]
        + [lines[i].replace("4", str(j + 4)) for j in range(n)]
        + lines[i + 1 :]
    )
    doc = "\n".join(lines).format(name, tag, section, params, *params_list)
    return type(name, (Expression,), {"tag": tag, "__doc__": doc})


UNARY_OPERATION_DOCSTRING = """PyMathML representation of the {1} unary operation.

    Usage: {0}(operand, **attributes)

    which produces the following MathML code:

        <mrow>
            <mo>{1}</mo>
            operand
        </mrow>
    """


def unary_operation_type(name, operator):
    """Return a class derived from UnaryOperation.

    The returned class is named name. The operator is specified as a
    string.
    """
    return type(
        name,
        (UnaryOperation,),
        {
            "operator": Operator(operator),
            "__doc__": UNARY_OPERATION_DOCSTRING.format(name, operator),
        },
    )


BINARY_OPERATION_DOCSTRING = """PyMathML representation of the {1} binary operation.

    Usage: {0}(*operands, **attributes)

    which produces the following MathML code (associativity is assumed):

        <mrow>
            operands[0]
            <mo>{1}</mo>
            operands[1]
            <mo>{1}</mo>
            operands[2]
            ...
        </mrow>
    """


def binary_operation_type(name, operator):
    """Return a class derived from BinaryOperation.

    The returned class is named name. The operator is specified as a
    string.
    """
    return type(
        name,
        (BinaryOperation,),
        {
            "operator": Operator(operator),
            "__doc__": BINARY_OPERATION_DOCSTRING.format(name, operator),
        },
    )


NARY_OPERATION_DOCSTRING = """PyMathML representation of the {1} n-ary operation.

    Usage: {0}(operand, start, end, **attributes)

    If both start and end are not None, the following MathML code is
    produced:

        <mrow>
            <munderover>
                <mo>{1}</mo>
                start
                end
            </munderover>
            operand
        </mrow>

    If only start is not None, the following MathML code is produced:

        <mrow>
            <munder>
                <mo>{1}</mo>
                start
            </munder>
            operand
        </mrow>

    Finally, if only end is not None, the following MathML code is
    produced:

        <mrow>
            <mover>
                <mo>{1}</mo>
                end
            </mover>
            operand
        </mrow>
    """


def nary_operation_type(name, operator):
    """Return a class derived from NaryOperation.

    The returned class is named name. The operator is specified as a
    string.
    """
    return type(
        name,
        (NaryOperation,),
        {
            "operator": Operator(operator),
            "__doc__": NARY_OPERATION_DOCSTRING.format(name, operator),
        },
    )


#
# Creation of classes derived from Token
# ======================================
#
Identifier = token_type("Identifier", "mi", "3.2.3")
Number = token_type("Number", "mn", "3.2.4")
Operator = token_type("Operator", "mo", "3.2.5")
Text = token_type("Text", "mtext", "3.2.6")

#
# Creation of classes derived from Expression
# ===========================================
#
# General layout schemata
# -----------------------
#
Row = expression_type("Row", "mrow", "3.3.1")
Frac = expression_type("Frac", "mfrac", "3.3.2", "numerator, denominator")
Sqrt = expression_type("Sqrt", "msqrt", "3.3.3", "base")
Root = expression_type("Root", "mroot", "3.3.3", "base, index")
Style = expression_type("Style", "mstyle", "3.3.4")
Fenced = expression_type("Fenced", "mfenced", "3.3.8")

#
# Script and limit schemata
# -------------------------
#
Sub = expression_type("Sub", "msub", "3.4.1", "base, subscript")
Sup = expression_type("Sup", "msup", "3.4.2", "base, superscript")
SubSup = expression_type("SubSup", "msubsup", "3.4.3", "base, subscript, superscript")
Under = expression_type("Under", "munder", "3.4.4", "base, underscript")
Over = expression_type("Over", "mover", "3.4.5", "base, overscript")
UnderOver = expression_type(
    "UnderOver", "munderover", "3.4.6", "base, underscript, overscript"
)

#
# Tables and matrices
# -------------------
#
Table = expression_type("Table", "mtable", "3.5.1")
TableRow = expression_type("TableRow", "mtr", "3.5.2")
TableEntry = expression_type("TableEntry", "mtd", "3.5.4", "entry")

#
# Unary, binary and n-ary operations
# ----------------------------------
#

Pos = unary_operation_type("Pos", "+")
Neg = unary_operation_type("Neg", "-")

Equals = binary_operation_type("Equals", "=")
Plus = binary_operation_type("Plus", "+")
Minus = binary_operation_type("Minus", "-")
Times = binary_operation_type("Times", "\N{MULTIPLICATION SIGN}")
InvisibleTimes = binary_operation_type("Times", "\N{INVISIBLE TIMES}")
Dot = binary_operation_type("Dot", "\N{DOT OPERATOR}")
CircledTimes = binary_operation_type("CircledTimes", "\N{CIRCLED TIMES}")
Div = binary_operation_type("Div", "/")

Product = nary_operation_type("Product", "\N{N-ARY PRODUCT}")
Sum = nary_operation_type("Sum", "\N{N-ARY SUMMATION}")


def expression(expr):
    """Convert expr to a PyMathML expression.

    The following conversion rules apply:

      - PyMathML expressions are returned unchanged,
      - numbers are converted to Number,
      - strings are converted to Identifier.

    In other cases, a ValueError is raised.
    """
    if expr is None:
        return None
    elif isinstance(expr, BaseExpression):
        return expr
    elif isinstance(expr, numbers.Number):
        return Number(expr)
    elif isinstance(expr, str):
        return Identifier(expr)
    else:
        raise ValueError(expr)


def tomathml(expr, display=None):
    """Convert expr to MathML.

    The MathML representation of expr is returned as a
    xml.etree.ElementTree.Element.

    If display is not None, then the expression is embedded into a math
    tag, with the specified 'display' attribute (namely: 'inline' or
    'block').
    """
    element = expression(expr).tomathml()
    if display is None:
        return element
    else:
        math = ET.Element(
            "math", xmlns="http://www.w3.org/1998/Math/MathML", display=str(display)
        )
        math.append(element)
        return math


def tostring(expr, display=None):
    """Return the MathML representation of expr as a string.

    The MathML representation of expr is returned as a string.

    If display is not None, then the expression is embedded into a math
    tag, with the specified 'display' attribute (namely: 'inline' or
    'block').
    """
    return ET.tostring(tomathml(expr, display), encoding="unicode")


def inline(expr):
    """Return the MathML representation of expr as a string.

    The expression is embedded into a math tag, with the 'display'
    attribute set to 'inline'.
    """
    return ET.tostring(tomathml(expr, "inline"), encoding="unicode")


def block(expr):
    """Return the MathML representation of expr as a string.

    The expression is embedded into a math tag, with the 'display'
    attribute set to 'block'.
    """
    return ET.tostring(tomathml(expr, "block"), encoding="unicode")


# Local Variables:
# fill-column: 72
# End:
