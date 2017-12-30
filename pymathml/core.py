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
        return Row(self, Operator('&ApplyFunction;'), Fenced(*args))

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
        """Initialize token element.

        The text of the resulting MathML token element is ``str(value)``.
        """
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


_DESCRIPTION_DOCSTRING = ('PyMathML implementation of the ``{}`` element.\n\n'
                          'See MathML specifications, section {}.')

_USAGE_DOCSTRING = ('Usage: ``{}({}, **attributes)``')


def create_token(name, tag, section):
    """Return a class derived from ``Token``

    TODO Docstring
    """
    docstring = _DESCRIPTION_DOCSTRING.format(tag, section)
    return type(name, (Token,), {'tag': tag, '__doc__': docstring})


def derive_expression(name, tag, section, params=None):
    doc = _DESCRIPTION_DOCSTRING.format(tag, section)
    usage = _USAGE_DOCSTRING.format(name, ', '.join(params) if params
                                    else '*expressions')
    dict = {'tag': tag, '__doc__': doc+'\n\n'+usage}
    return type(name, (Expression,), dict)


# Token elements
Identifier = create_token('Identifier', 'mi', '3.2.3')
Number = create_token('Number', 'mn', '3.2.4')
Operator = create_token('Operator', 'mo', '3.2.5')
Text = create_token('Text', 'mtext', '3.2.6')

# General layout schemata
Row = derive_expression('Row', 'mrow', '3.3.1')
Frac = derive_expression('Frac', 'mfrac', '3.3.2',
                         ['numerator', 'denominator'])
Sqrt = derive_expression('Sqrt', 'msqrt', '3.3.3', ['base'])
Root = derive_expression('Root', 'mroot', '3.3.3', ['base', 'index'])
Style = derive_expression('Style', 'mstyle', '3.3.4')
Fenced = derive_expression('Fenced', 'mfenced', '3.3.8')

# Script and limit schemata
Sub = derive_expression('Sub', 'msub', '3.4.1', ['base', 'subscript'])
Sup = derive_expression('Sup', 'msup', '3.4.2', ['base', 'superscript'])
SubSup = derive_expression('SubSup', 'msubsup', '3.4.3',
                           ['base', 'subscript', 'superscript'])
Under = derive_expression('Under', 'munder', '3.4.4', ['base', 'underscript'])
Over = derive_expression('Over', 'mover', '3.4.5', ['base', 'overscript'])
UnderOver = derive_expression('UnderOver', 'munderover', '3.4.6',
                              ['base', 'underscript', 'overscript'])

# Tables and matrices
Table = derive_expression('Table', 'mtable', '3.5.1')
TableRow = derive_expression('TableRow', 'mtr', '3.5.2')
TableEntry = derive_expression('TableEntry', 'mtd', '3.5.4', ['entry'])


class BinaryOperation(Expression):
    def to_mml(self):
        children = [self.children[0]]
        for child in self.children[1:]:
            children.append(self.op)
            children.append(child)
        return Row(*children).to_mml()


class UnaryOperation(Expression):
    def __init__(self, child, **attributes):
        super().__init__(child, **attributes)

    def to_mml(self):
        return Row(self.op, self.children[0], **self.attributes).to_mml()


class NaryOperation(Expression):
    def __init__(self, expr, start, end, **attributes):
        super().__init__(expr, start, end, **attributes)

    def to_mml(self):
        expr, start, end = self.children
        op = self.op
        if end is None:
            if start:
                op = Under(self.op, start)
        else:
            if start is None:
                op = Over(self.op, end)
            else:
                op = UnderOver(self.op, start, end)
        return Row(op, expr, **self.attributes).to_mml()


class Neg(UnaryOperation):
    op = Operator('-')


class Pos(UnaryOperation):
    op = Operator('+')


class Equals(BinaryOperation):
    op = Operator('=')


class Plus(BinaryOperation):
    op = Operator('+')


class Minus(BinaryOperation):
    op = Operator('-')


class Times(BinaryOperation):
    op = Operator('&InvisibleTimes;')


class Sum(NaryOperation):
    op = Operator('&Sum;')


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
