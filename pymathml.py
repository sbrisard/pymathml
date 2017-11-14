import numbers
import xml.etree.ElementTree as ET

INVISIBLE_TIMES = '\N{INVISIBLE TIMES}'
FUNCTION_APPLICATION = '\N{FUNCTION APPLICATION}'


class Expression:
    def __init__(self, *expressions, **attributes):
        self.children = expressions
        self.attributes = attributes

    def to_mml(self):
        e = ET.Element(self.tag, self.attributes)
        for child in self.children:
            e.append(to_mml(child))
        return e

    def __add__(self, other):
        return Add(self, expression(other))

    def __radd__(self, other):
        return Add(expression(other), self)

    def __sub__(self, other):
        return Sub(self, expression(other))

    def __rsub__(self, other):
        return Add(expression(other), self)

    def __mul__(self, other):
        return Mul(self, expression(other))

    def __rmul__(self, other):
        return Mul(expression(other), self)

    def __pow__(self, other):
        return Power(self, expression(other))

    def __getitem__(self, key):
        subscript = (Fenced(*key, open='', close='')
                     if isinstance(key, tuple) else expression(key))
        return Subscript(self, subscript)

    def __call__(self, *args):
        return Group(self, Operator(FUNCTION_APPLICATION), Fenced(*args))


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


class Group(Expression):
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
        return to_mml(Group(*children))


class Add(Operation):
    op = Operator('+')


class Sub(Operation):
    op = Operator('-')


class Mul(Operation):
    op = Operator(INVISIBLE_TIMES)


class Power(Expression):
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent

    def to_mml(self):
        e = ET.Element('msup')
        if isinstance(self.base, Token):
            e.append(self.base.to_mml())
        else:
            e.append(Fenced(self.base).to_mml())
        e.append(self.exponent.to_mml())
        return e


class Subscript(Expression):
    def __init__(self, base, subscript):
        self.base = base
        self.subscript = subscript

    def to_mml(self):
        e = ET.Element('msub')
        e.append(to_mml(self.base))
        e.append(to_mml(self.subscript))
        return e


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
    #xc = Identifier('c')
    x = Identifier('x')
    y = Identifier('y')
    Delta = b**2-4*a*'c'
    expr = Frac(b-Root(Delta, 2), 2*a)
    #expr = (a(x, y)+b[4, 5]+x+y-x-3*y*a)**2
    mml = expr.to_mml()
    ET.dump(mml)
    tree = block_mml(expr)
    tree.write('essai.mml')
