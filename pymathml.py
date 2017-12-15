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
    behave almost like true mathematical expression. One notable
    exception is automatic parenthetizing, which is *not*
    implemented. Therefore, this code:

        a, b = identifiers('a', 'b')
        (a+b)**2

    would be translated to the following MathML

        <mrow><mi>a</mi><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow>

    which in fact renders as

        a+b²

    This class should *not* be instantiated directly. Use derived
    classes instead.

    Developers should note that derived classes *must* implement a
    to_mml function.

    """
    def __add__(self, other):
        return Plus(self, expression(other))

    def __radd__(self, other):
        return Plus(expression(other), self)

    def __sub__(self, other):
        return Minus(self, expression(other))

    def __rsub__(self, other):
        return Minus(expression(other), self)

    def __mul__(self, other):
        return Times(self, expression(other))

    def __rmul__(self, other):
        return Times(expression(other), self)

    def __pow__(self, other):
        return Sup(self, expression(other))

    def __neg__(self):
        return Neg(self)

    def __pos__(self):
        return Pos(self)

    def __getitem__(self, key):
        subscript = (Fenced(*key, open='', close='')
                     if isinstance(key, tuple) else expression(key))
        return Sub(self, subscript)

    def __call__(self, *args):
        return Row(self, Operator('&ApplyFunction;'), Fenced(*args))


class Token(BaseExpression):
    """Token elements in the sense of the MathML specifications (§3.1.9.1).


    """
    def __init__(self, value, **attributes):
        self.value = value
        self.attributes = attributes

    def to_mml(self):
        return to_xml_string(self.tag, text=str(self.value), **self.attributes)


class Expression(BaseExpression):
    def __init__(self, *expressions, **attributes):
        self.children = expressions
        self.attributes = attributes

    def to_mml(self):
        """Return the MathML representation of this object as a string.

        """
        return to_xml_string(self.tag,
                             children=[to_mml(c) for c in self.children],
                             **self.attributes)


class Identifier(Token):
    tag = 'mi'


class Number(Token):
    tag = 'mn'


class Operator(Token):
    tag = 'mo'


class Text(Token):
    tag = 'mtext'


class Row(Expression):
    tag = 'mrow'


class Frac(Expression):
    tag = 'mfrac'

    def __init__(self, numerator, denominator, **attributes):
        super().__init__(numerator, denominator, **attributes)


class Sqrt(Expression):
    tag = 'msqrt'

    def __init__(self, base, **attributes):
        super().__init__(base, **attributes)


class Root(Expression):
    tag = 'mroot'

    def __init__(self, base, index, **attributes):
        super().__init__(base, index, **attributes)


class Style(Expression):
    tag = 'mstyle'


class Fenced(Expression):
    tag = 'mfenced'


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


def underbrace(expression, underscript):
    return Under(expression,
                 Under(Operator('&UnderBrace;'),
                       underscript, accentunder='true'))


def table(rows, **attributes):
    return Table(*[TableRow(*[TableEntry(e) for e in r]) for r in rows],
                 **attributes)


def requires_fences(expr):
    if isinstance(expr, Token):
        return False
    if isinstance(expr, Fenced):
        return False
    return True


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


if __name__ == '__main__':
    p, i, j, m, n = identifiers('p', 'i', 'j', 'm', 'n')
    Ep = Identifier('E')[Text('p')]

    lhs = Row(Ep(p), Operator('='))
    rhs1 = underbrace(Fenced(p[m-1, 0]-p[0, 0])**2
                      +Fenced(p[0, n-1]-p[0, 0])**2,
                      'top-left corner')
    rhs2 = +underbrace(Fenced(p[0, 0]-p[0, n-1])**2
                       +Fenced(p[m-1, n-1]-p[0, n-1])**2,
                       'top-right corner')
    t = table([[lhs, rhs1], [None, rhs2]],
              columnspacing='0em',
              columnalign='right left',
              displaystyle='true')

    with open('essai.html', 'w', encoding='utf8') as f:
        f.write('<html><body>')
        f.write(to_mml(t, display='block'))
        f.write('</body></html>')
