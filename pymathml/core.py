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


class Identifier(Token):
    """PyMathML implementation of the ``mi`` token element.

    See MathML specifications, section 3.2.3.
    """

    tag = 'mi'


class Number(Token):
    """PyMathML implementation of the ``mn`` token element.

    See MathML specifications, section 3.2.4.
    """

    tag = 'mn'


class Operator(Token):
    """PyMathML implementation of the ``mo`` token element.

    See MathML specifications, section 3.2.5.
    """

    tag = 'mo'


class Text(Token):
    """PyMathML implementation of the ``mtext`` token element.

    See MathML specifications, section 3.2.6.
    """

    tag = 'mtext'


class Row(Expression):
    """PyMathML implementation of the ``mrow`` element.

    See MathML specifications, section 3.3.1.
    """

    tag = 'mrow'


class Frac(Expression):
    """PyMathML implementation of the ``mfrac`` element.

    See MathML specifications, section 3.3.2.
    """

    tag = 'mfrac'

    def __init__(self, numerator, denominator, **attributes):
        super().__init__(numerator, denominator, **attributes)


class Sqrt(Expression):
    """PyMathML implementation of the ``msqrt`` element.

    See MathML specifications, section 3.3.3.
    """

    tag = 'msqrt'

    def __init__(self, base, **attributes):
        super().__init__(base, **attributes)


class Root(Expression):
    """PyMathML implementation of the ``mroot`` element.

    See MathML specifications, section 3.3.3.
    """

    tag = 'mroot'

    def __init__(self, base, index, **attributes):
        super().__init__(base, index, **attributes)


class Style(Expression):
    """PyMathML implementation of the ``mstyle`` element.

    See MathML specifications, section 3.3.4.
    """

    tag = 'mstyle'


class Fenced(Expression):
    """PyMathML implementation of the ``mfenced`` element.

    See MathML specifications, section 3.3.8.
    """

    tag = 'mfenced'


class Sub(Expression):
    tag = 'msub'

    def __init__(self, base, subscript, **attributes):
        super().__init__(base, subscript, **attributes)


class Sup(Expression):
    tag = 'msup'

    def __init__(self, base, superscript, **attributes):
        super().__init__(base, superscript, **attributes)


class SubSup(Expression):
    tag = 'msubsup'

    def __init__(self, base, subscript, superscript, **attributes):
        super().__init__(base, subscript, superscript, **attributes)


class Under(Expression):
    tag = 'munder'

    def __init__(self, base, underscript, **attributes):
        super().__init__(base, underscript, **attributes)


class Over(Expression):
    tag = 'mover'

    def __init__(self, base, overscript, **attributes):
        super().__init__(base, overscript, **attributes)


class UnderOver(Expression):
    tag = 'munderover'

    def __init__(self, base, underscript, overscript, **attributes):
        super().__init__(base, underscript, overscript, **attributes)


class Table(Expression):
    tag = 'mtable'


class TableRow(Expression):
    tag = 'mtr'


class TableEntry(Expression):
    tag = 'mtd'

    def __init__(self, entry, **attributes):
        super().__init__(entry, **attributes)


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
