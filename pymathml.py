import numbers
import xml.etree.ElementTree as ET

INVISIBLE_TIMES = '\N{INVISIBLE TIMES}'
FUNCTION_APPLICATION = '\N{FUNCTION APPLICATION}'


class Expression:
    def __init__(self, *expressions, **attributes):
        self.children = expressions
        self.attributes = attributes

    def to_mml(self):
        tag = self.tag if hasattr(self, 'tag') else type(self).__name__
        e = ET.Element(tag, self.attributes)
        for child in self.children:
            e.append(to_mml(child))
        return e

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
        return Row(self, Operator(FUNCTION_APPLICATION), Fenced(*args))


class Token(Expression):
    def __init__(self, value, **attributes):
        self.value = value
        self.attributes = attributes

    def to_mml(self):
        e = ET.Element(self.tag)
        e.text = str(self.value)
        return e


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


class Operation(Expression):
    def __init__(self, *children):
        self.children = children

    def to_mml(self):
        children = [self.children[0]]
        for child in self.children[1:]:
            children.append(self.op)
            children.append(child)
        return to_mml(Row(*children))


class UnaryOperation(Expression):
    def __init__(self, child, **attributes):
        super().__init__(child, **attributes)

    def to_mml(self):
        return to_mml(Row(self.op, self.children[0], **self.attributes))


class Plus(Operation):
    op = Operator('+')


class Minus(Operation):
    op = Operator('-')


class Times(Operation):
    op = Operator(INVISIBLE_TIMES)


class Neg(UnaryOperation):
    op = Operator('-')


class Pos(UnaryOperation):
    op = Operator('+')


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

def to_mml(expr):
    if hasattr(expr, 'to_mml'):
        return expr.to_mml()
    elif isinstance(expr, numbers.Number):
        return Number(expr).to_mml()
    elif isinstance(expr, str):
        return Identifier(expr).to_mml()
    else:
        raise ValueError(expr)


def expression(expr):
    if isinstance(expr, Expression):
        return expr
    elif isinstance(expr, numbers.Number):
        return Number(expr)
    elif isinstance(expr, str):
        return Identifier(expr)
    else:
        raise ValueError()


def block_mml(expr):
    math = ET.Element('math',
                      xmlns='http://www.w3.org/1998/Math/MathML',
                      display='block')
    math.append(expr.to_mml())
    return ET.ElementTree(math)


if __name__ == '__main__':
    one = Number(1)
    two = Number(2)
    a = Identifier('a')
    b = Identifier('b')
    c = Identifier('c')
    x = Identifier('x')
    y = Identifier('y')
    Delta = b**2-4*a*'c'
    #expr = x[1, 2]+SubSup(y, 1, 2)+Frac(b-Root(Delta, 2), 2*a)
    #expr = (a(x, y)+b[4, 5]+x+y-x-3*y*a)**2
    expr = Frac(+b-Sqrt(b**2-4*a*c), a)
    mml = expr.to_mml()
    ET.dump(mml)
    tree = block_mml(expr)
    tree.write('essai.mml')
    print(type(tree).__name__)
    print(type(a).__name__)
