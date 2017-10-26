import numbers
import xml.etree.ElementTree as ET


class Expression:
    def __add__(self, other):
        return Add(self, expression(other))

    def __pow__(self, other):
        return Power(self, expression(other))

    def __getitem__(self, key):
        return Sub(self, key)


class Atom(Expression):
    pass


class Number(Atom):
    def __init__(self, value):
        self.value = value

    def to_mml(self):
        e = ET.Element('mn')
        e.text = str(self.value)
        return e


class Identifier(Atom):
    def __init__(self, name):
        self.name = name

    def to_mml(self):
        e = ET.Element('mi')
        e.text = str(self.name)
        return e


class Add(Expression):
    def __init__(self, elt1, elt2, *elts):
        self.children = [elt1, elt2]+list(elts)
        # TODO This should be a class variable
        self.mo = ET.Element('mo')
        self.mo.text = '+'

    def to_mml(self):
        e = ET.Element('mrow')
        it = iter(self.children)
        e.append(next(it).to_mml())
        for child in it:
            e.append(self.mo)
            e.append(child.to_mml())
        return e


class Fenced(Expression):
    def __init__(self, expr):
        self.child = expr

    def to_mml(self):
        e = ET.Element('mfenced')
        e.append(self.child.to_mml())
        return e


class Power(Expression):
    def __init__(self, base, exponent):
        self.base = base
        self.exponent = exponent

    def to_mml(self):
        e = ET.Element('msup')
        if isinstance(self.base, Atom):
            e.append(self.base.to_mml())
        else:
            e.append(Fenced(self.base).to_mml())
        e.append(self.exponent.to_mml())
        return e


class Sub(Expression):
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
    expr = (a+b[4])**2
    mml = expr.to_mml()
    ET.dump(mml)
    tree = block_mml(expr)
    tree.write('essai.mml')
