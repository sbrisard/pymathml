import numbers

def xml_element(tag, *children, text=None, **attributes):
    if text is None:
        text = ''
    if attributes == {}:
        attr = ''
    else:
        attr = ' '+' '.join('{}="{}"'.format(k, str(v))
                            for k, v in attributes.items())
    if attributes is None:
        attr = ''
    s = u'<{0}{1}>{2}{3}</{0}>'.format(tag, attr,
                                       ''.join(str(c) for c in children),
                                       str(text))
    return s


class Expression:
    def __init__(self, *expressions, **attributes):
        self.children = expressions
        self.attributes = attributes

    def to_mml(self):
        """Return the MathML representation of this object as a string.

        """
        return xml_element(self.tag,
                           *[to_mml(child) for child in self.children],
                           **self.attributes)

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


class Token(Expression):
    def __init__(self, value, **attributes):
        self.value = value
        self.attributes = attributes

    def to_mml(self):
        return xml_element(self.tag, text=str(self.value), **self.attributes)


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
    def __init__(self, *children):
        self.children = children

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


def expression(expr):
    if isinstance(expr, Expression):
        return expr
    elif isinstance(expr, numbers.Number):
        return Number(expr)
    elif isinstance(expr, str):
        return Identifier(expr)
    else:
        raise ValueError()


def identifiers(*names, **attributes):
    """Return instances of Identifier with specified names.

    All returned instances of class Identifier have same attributes.
    """
    return tuple(Identifier(name, **attributes) for name in names)


def to_mml(expr, display=None):
    """Return the MathML code for the specified expression.

    The MathML code is returned as an ``ElementTree.Element``.

    If `display` is not ``None``, then the expression is embedded into
    a ``math`` tag, with the specified 'display' attribute (namely:
    'inline' or 'block').  If `mode` is 'plain', then the returned

    """
    e = expression(expr).to_mml()
    if display is None:
        return e
    else:
        return xml_element('math', e,
                           xmlns='http://www.w3.org/1998/Math/MathML',
                           display=str(display))


if __name__ == '__main__':
    one = Number(1)
    two = Number(2)
    a = Identifier('a')
    b = Identifier('b')
    c = Identifier('c')
    x = Identifier('x')
    y = Identifier('y')
    n = Identifier('n')
    Delta = b**2-4*a*'c'
    #expr = x[1, 2]+SubSup(y, 1, 2)+Frac(b-Root(Delta, 2), 2*a)
    #expr = (a(x, y)+b[4, 5]+x+y-x-3*y*a)**2
    #expr = Frac(+b-Sqrt(b**2-4*a*c), a)
    expr = Sum(Frac(1, n**2), 1, 'N')

    p, i, m, n = identifiers('p', 'i', 'm', 'n')
    expr = Sum(Fenced(2*p[i, n-1]-p[i, 0])**2, Equals(i, 1), m-2)

    underbrace = Operator('&UnderBrace;')
    expr = Under(expr,
                 Under(underbrace, Text('top-left corner', accentunder='true')))
    with open('essai.html', 'w', encoding='utf8') as f:
        f.write('<html><body>')
        f.write(to_mml(expr, display='block'))
        f.write('</body></html>')
