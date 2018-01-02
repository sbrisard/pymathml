import numbers


def to_xml_string(tag, text=None, children=None, **attributes):
    if text is None:
        text = ''
    attributes_str = ('' if attributes == {}
                      else (' '+' '.join('{}="{}"'.format(k, str(v))
                                         for k, v in attributes.items())))
    children_str = ('' if children is None
                    else ''.join(str(c) for c in children))
    s = u'<{0}{1}>{2}{3}</{0}>'.format(tag, attributes_str, children_str,
                                       str(text))
    return s


class BaseExpression:
    """Base class for MathML expressions.

    This class defines all magical functions that allow instances to
    behave almost like true mathematical expressions (see table below).

    Python-to-MathML conversion guide:

    In the table below, ``e``, ``e1`` and ``e2`` are PyMathML
    expressions, ``me``, ``me1`` and ``me2`` are their translation to
    MathML, resulting from a call to ``to_mathml``.

    ========== ======================================================
    Python     MathML
    ========== ======================================================
    ``+e``     ``<mrow><mo>+</mo>me</mrow>``
    ``-e``     ``<mrow><mo>-</mo>me</mrow>``
    ``e1+e2``  ``<mrow>me1<mo>+</mo>me2</mrow>``
    ``e1-e2``  ``<mrow>me1<mo>-</mo>me2</mrow>``
    ``e1*e2``  ``<mrow>me1<mo>&it;</mo>me2</mrow>``
    ``e1**e2`` ``<msup>me1 me2</msup>``
    ``e1[e2]`` ``<msub>me1 me2</msub>``
    ``e1(e2)`` ``<mrow>me1<mo>&af;</mo><mfenced>e2</mfenced></mrow>``
    ========== ======================================================

    This class does not provide an initializer and should *not* be
    instantiated directly. Use derived classes instead.
    """

    def __add__(self, other):
        return Plus(self, other)

    def __radd__(self, other):
        return Plus(other, self)

    def __sub__(self, other):
        return Minus(self, other)

    def __rsub__(self, other):
        return Minus(other, self)

    def __mul__(self, other):
        return Times(self, other)

    def __rmul__(self, other):
        return Times(other, self)

    def __pow__(self, other):
        return Sup(self, other)

    def __neg__(self):
        return Neg(self)

    def __pos__(self):
        return Pos(self)

    def __getitem__(self, key):
        subscript = (Fenced(*key, open='', close='')
                     if isinstance(key, tuple) else key)
        return Sub(self, subscript)

    def __call__(self, *args):
        return Row(self, Operator('\N{FUNCTION APPLICATION}'), Fenced(*args))

    def to_mml(self):
        """Return the MathML representation of this object as a string."""
        raise NotImplementedError('sub-classes of BaseExpression should'
                                  ' implement this method')


class Token(BaseExpression):
    """Token elements (see MathML specifications, section 3.1.9.1).

    This class should *not* be instanciated directly. Use derived
    classes instead (listed below, together with their MathML
    translation).

    ================= ====================
    PyMathML          MathML
    ================= ====================
    Identifier        <mi>...</mi>
    Number            <mn>...</mn>
    Operator          <mo>...</mo>
    Text              <mtext>...</mtext>
    *not implemented* <mspace>...</mspace>
    *not implemented* <ms>...</ms>
    ================= ====================
    """

    def __init__(self, value, **attributes):
        """Initialize token element."""
        self.value = value
        self.attributes = attributes

    def to_mml(self):
        return to_xml_string(self.tag, text=str(self.value), **self.attributes)


class Expression(BaseExpression):
    """Base class for non-token elements.

    This class is the base class for the following element types

      - general layout schemata,
      - script and limit schemata,
      - tables and matrices.

    This class should *not* be instanciated directly. Use derived
    classes instead (listed below, together with their MathML
    translation).

    General Layout Schemata
    -----------------------

    See MathML specifications, section 3.1.9.2.

    ======== =================
    MathML   PyMathML
    ======== =================
    mrow     Row
    mfrac    Frac
    msqrt    Sqrt
    mroot    Root
    mstyle   Style
    merror   *not implemented*
    mpadded  *not implemented*
    mphantom *not implemented*
    mfenced  Fenced
    menclose *not implemented*
    ======== =================

    Script and Limit Schemata
    -------------------------

    See MathML specifications, section 3.1.9.3.

    ============= =================
    MathML        PyMathML
    ============= =================
    msub          Sub
    msup          Sup
    msubsup       SubSup
    munder        Under
    mover         Over
    munderover    UnderOver
    mmultiscripts *not implemented*
    ============= =================

    Tables and matrices
    -------------------

    See MathML specifications, section 3.1.9.4.

    =========== =================
    MathML      PyMathML
    =========== =================
    mtable      Table
    mlabeledtr  *not implemented*
    mtr         TableRow
    mtd         TableEntry
    maligngroup *not implemented*
    malignmark  *not implemented*
    =========== =================
    """
    def __init__(self, *expressions, **attributes):
        """Initialize expression.

        ``*expressions`` are the children of the resulting MathML
        element. They are automatically converted to ``Expression``
        using the function ``expression``.

        """
        self.children = [expression(e) for e in expressions]
        self.attributes = attributes

    def to_mml(self):
        return to_xml_string(self.tag,
                             children=[to_mml(c) for c in self.children],
                             **self.attributes)


class UnaryOperation(Expression):
    """PyMathML representation of unary operations.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """
    def to_mml(self):
        return Row(self.operator, self.children[0], **self.attributes).to_mml()


class BinaryOperation(Expression):
    """PyMathML representation of a binary operation.

    Assuming associativity, the binary operator can be applied to more
    than two operands. They are enclosed in a ``mrow`` element.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """
    def to_mml(self):
        children = [self.children[0]]
        for child in self.children[1:]:
            children.append(self.operator)
            children.append(child)
        return Row(*children).to_mml()


class NaryOperation(Expression):
    """PyMathML representation of a n-ary operation.

    This class should *not* be instanciated directly. Use derived
    classes instead.
    """
    def to_mml(self):
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
        return Row(operator, expr, **self.attributes).to_mml()


#
# Automatic creation of derived classes
# =====================================
#
TOKEN_DOCSTRING = (
    """PyMathML representation of the ``{1}`` token element.

    See MathML specifications, section {2}.

    Usage: ``{0}(value, **attributes)``

    which produces the following MathML code

        <{1}>str(value)</{1}>

    (note the call to ``str``).
    """)


def token_type(name, tag, section):
    """Return a class derived from ``Token``.

    The returned class is named ``name``. The docstring refers to the
    specified ``section`` of the MathML specifications.
    """
    return type(name, (Token,),
                {'tag': tag,
                 '__doc__': TOKEN_DOCSTRING.format(name, tag, section)})


EXPRESSION_DOCSTRING = (
    """PyMathML representation of the ``{1}`` element.

    See MathML specifications, section {2}.

    Usage: ``{0}({3}, **attributes)``

    which produces the following MathML code

        <{1}>
            {4}
        </{1}>
    """)


def expression_type(name, tag, section, params=None):
    """Return a class derived from ``Expression``.

    The returned class is named ``name``. The docstring refers to the
    specified ``section`` of the MathML specifications. The "usage"
    section of the docstring lists the ``params`` of the initializer
    (``*expressions`` if not specified).
    """
    placeholder = '{4}'
    doc = EXPRESSION_DOCSTRING
    if params is None:
        params_list = ['to_mml(expressions[0])',
                       'to_mml(expressions[1])',
                       '...']
    else:
        params_list = ['to_mml({})'.format(s.strip())
                       for s in params.split(',')]
    n = len(params_list)
    lines = doc.splitlines()
    for i, s in enumerate(lines):
        if placeholder in s:
            break
    lines = (lines[:i]+[lines[i].replace('4', str(j+4)) for j in range(n)]
             + lines[i+1:])
    doc = '\n'.join(lines).format(name, tag, section, params, *params_list)
    return type(name, (Expression,), {'tag': tag, '__doc__': doc})


UNARY_OPERATION_DOCSTRING = (
    """PyMathML representation of the ``{1}`` unary operation.

    Usage: ``{0}(operand, **attributes)``

    which produces the following MathML code (associativity is assumed)

        <mrow>
            <mo>{1}</mo>
            operand
        </mrow>
    """)


def unary_operation_type(name, operator):
    """Return a class derived from ``UnaryOperation``.

    The returned class is named ``name``. The ``operator`` is specified
    as a string.
    """
    return type(name, (UnaryOperation,),
                {'operator': Operator(operator),
                 '__doc__': UNARY_OPERATION_DOCSTRING.format(name, operator)})


BINARY_OPERATION_DOCSTRING = (
    """PyMathML representation of the ``{1}`` binary operation.

    Usage: ``{0}(*operands, **attributes)``

    which produces the following MathML code (associativity is assumed)

        <mrow>
            operands[0]
            <mo>{1}</mo>
            operands[1]
            <mo>{1}</mo>
            operands[2]
            ...
        </mrow>
    """)


def binary_operation_type(name, operator):
    """Return a class derived from ``BinaryOperation``.

    The returned class is named ``name``. The ``operator`` is specified
    as a string.
    """
    return type(name, (BinaryOperation,),
                {'operator': Operator(operator),
                 '__doc__': BINARY_OPERATION_DOCSTRING.format(name, operator)})


NARY_OPERATION_DOCSTRING = (
    """PyMathML representation of the ``{1}`` n-ary operation.

    Usage: ``{0}(operand, start, end, **attributes)``

    If both ``start`` and ``end`` are specified, the following MathML
    code is produced

        <mrow>
            <munderover>
                <mo>{1}</mo>
                start
                end
            </munderover>
            operand
        </mrow>

    If only ``start`` is specified, the following MathML code is produced

        <mrow>
            <munder>
                <mo>{1}</mo>
                start
            </munder>
            operand
        </mrow>

    Finally, if only ``end`` is specified, the following MathML code is
    produced

        <mrow>
            <mover>
                <mo>{1}</mo>
                end
            </mover>
            operand
        </mrow>
    """)


def nary_operation_type(name, operator):
    """Return a class derived from ``NaryOperation``.

    The returned class is named ``name``. The ``operator`` is specified
    as a string.
    """
    return type(name, (NaryOperation,),
                {'operator': Operator(operator),
                 '__doc__': NARY_OPERATION_DOCSTRING.format(name, operator)})


#
# Creation of classes derived from Token
# ======================================
#
Identifier = token_type('Identifier', 'mi', '3.2.3')
Number = token_type('Number', 'mn', '3.2.4')
Operator = token_type('Operator', 'mo', '3.2.5')
Text = token_type('Text', 'mtext', '3.2.6')

#
# Creation of classes derived from Expression
# ===========================================
#
# General layout schemata
# -----------------------
#
Row = expression_type('Row', 'mrow', '3.3.1')
Frac = expression_type('Frac', 'mfrac', '3.3.2', 'numerator, denominator')
Sqrt = expression_type('Sqrt', 'msqrt', '3.3.3', 'base')
Root = expression_type('Root', 'mroot', '3.3.3', 'base, index')
Style = expression_type('Style', 'mstyle', '3.3.4')
Fenced = expression_type('Fenced', 'mfenced', '3.3.8')

#
# Script and limit schemata
# -------------------------
#
Sub = expression_type('Sub', 'msub', '3.4.1', 'base, subscript')
Sup = expression_type('Sup', 'msup', '3.4.2', 'base, superscript')
SubSup = expression_type('SubSup', 'msubsup', '3.4.3',
                         'base, subscript, superscript')
Under = expression_type('Under', 'munder', '3.4.4', 'base, underscript')
Over = expression_type('Over', 'mover', '3.4.5', 'base, overscript')
UnderOver = expression_type('UnderOver', 'munderover', '3.4.6',
                            'base, underscript, overscript')

#
# Tables and matrices
# -------------------
#
Table = expression_type('Table', 'mtable', '3.5.1')
TableRow = expression_type('TableRow', 'mtr', '3.5.2')
TableEntry = expression_type('TableEntry', 'mtd', '3.5.4', 'entry')

#
# Unary, binary and n-ary operations
# ----------------------------------
#

Pos = unary_operation_type('Pos', '+')
Neg = unary_operation_type('Neg', '-')

Equals = binary_operation_type('Equals', '=')
Plus = binary_operation_type('Plus', '+')
Minus = binary_operation_type('Minus', '-')
Times = binary_operation_type('Times', '\N{INVISIBLE TIMES}')

Sum = nary_operation_type('Sum', '\N{N-ARY SUMMATION}')


def expression(expr):
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


def identifiers(*names, **attributes):
    """Return instances of Identifier with specified names.

    All returned instances of class Identifier have same attributes.
    """
    return tuple(Identifier(name, **attributes) for name in names)


def to_mml(expr, display=None):
    """Return the MathML code for the specified expression, as a string.

    If `display` is not ``None``, then the expression is embedded into
    a ``math`` tag, with the specified 'display' attribute (namely:
    'inline' or 'block').
    """
    e = '' if expr is None else expression(expr).to_mml()
    if display is None:
        return e
    else:
        return to_xml_string('math', children=[e],
                             xmlns='http://www.w3.org/1998/Math/MathML',
                             display=str(display))


# Local Variables:
# fill-column: 72
# End:
