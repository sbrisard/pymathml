
# PyMathML

PyMathML is a Python package to create MathML expressions programatically.

The present version of PyMathML is restricted to *Presentation MathML* (see
MathML specifications, [chapter 3](https://www.w3.org/TR/MathML3/chapter3.html)).

MathML is extremely verbose; with PyMathML, concise, pythonic expressions are
converted to valid, well-formed MathML code. For example, the following snippet:


```python
from pymathml import *
from pymathml.utils import *
```


```python
a, b = identifiers('a', 'b')
expr = a**2+2*a*b+b**2
```

defines the mathematical expression ``a²+2ab+b²``. PyMathML then produces the following MathML code


```python
print(expr)
```

    <mrow><mrow><msup><mi>a</mi><mn>2</mn></msup><mo>+</mo><mrow><mrow><mn>2</mn><mo>⁢</mo><mi>a</mi></mrow><mo>⁢</mo><mi>b</mi></mrow></mrow><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow>
    

*This code is released under a BSD 3-clause "New" or "Revised" License. It is
open to contributions.*

To install PyMathML, clone this repository and issue the following command:

    python setyp.py install

The remainder of this page is a tutorial. It is organized as follows:
  
  - [Converting PyMathML expressions to MathML](#Converting-PyMathML-expressions-to-MathML)
  - [Basic MathML elements](#Basic-MathML-elements)
    - [Token elements](#Token-elements)
    - [Non-token elements](#Non-token-elements)
  - [Building complex expressions with special methods](#Building-complex-expressions-with-special-methods)
  - [Mathematical operations](#Mathematical-operations)
    - [Unary operations](#Unary-operations)
    - [Binary operations](#Binary-operations)
    - [N-ary operations](#N-ary-operations)
    
This ``README.md`` is the Markdown export of a Jupyter Notebook which can be
found in the ``docs/`` directory of this repository.


```python
import inspect # This will be used below
```

## Converting PyMathML expressions to MathML

Let us define a basic PyMathML expression:


```python
a, b, c, x = identifiers('a', 'b', 'c', 'x')
expr = a*x**2+b*x+c # ax²+bx+c
```

Then ``str(expr)`` returns its MathML representation:


```python
str(expr)
```




    '<mrow><mrow><mrow><mi>a</mi><mo>\u2062</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>\u2062</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow>'



PyMathML expressions can be displayed (using MathJax) in Jupyter notebooks
(note: owing to limitations of Github Flavored Markdown, you really need to
execute the Jupyter Notebook in the ``docs/`` directory to see the output of
this cell properly).


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mrow><mrow><mi>a</mi><mo>⁢</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>⁢</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow></math>



``expr.tomathml()`` returns the MathML representation of ``expr`` as an
``Element`` from the ``xml.etree.ElementTree`` module in the
[standard library](https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree):


```python
mml = expr.tomathml()
type(mml)
```




    xml.etree.ElementTree.Element



which can then be converted to XML as follows:


```python
import xml.etree.ElementTree as ET

print(ET.tostring(mml, encoding='unicode'))
```

    <mrow><mrow><mrow><mi>a</mi><mo>⁢</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>⁢</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow>
    

The function ``tomathml`` promotes its argument to a PyMathML expression, and
calls the ``tomathml()`` method:


```python
mml = tomathml('a')
print(ET.tostring(mml, encoding=('unicode')))
```

    <mi>a</mi>
    

If the optional argument ``display`` is specified, the expression is enclosed
in a ``math`` element, with the specified ``display`` attribute:


```python
mml = tomathml('a', display='block')
print(ET.tostring(mml, encoding=('unicode')))
```

    <math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mi>a</mi></math>
    


```python
mml = tomathml('a', display='inline')
print(ET.tostring(mml, encoding=('unicode')))
```

    <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><mi>a</mi></math>
    

The function ``tostring`` promotes its argument to a PyMathML expression, and
returns its MathML representation as a string. It takes the same optional
argument ``display`` as the ``tomathml`` function:


```python
tostring('a')
```




    '<mi>a</mi>'




```python
tostring('a', display='block')
```




    '<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mi>a</mi></math>'




```python
tostring('a', display='inline')
```




    '<math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><mi>a</mi></math>'




## Basic MathML elements

All MathML elements are defined as PyMathML objects.

### Token elements

Token elements are MathML elements that have text, but no children (see MathML
specifications,
[section 3.1.9.1](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.1)).
Token elements all derive from the ``Token`` class (see conversion table below).

| MathML     | PyMathML          |
|------------|------------------ |
| ``mi``     | ``Identifier``    |
| ``mn``     | ``Number``        |
| ``mo``     | ``Operator``      |
| ``mtext``  | ``Text``          |
| ``mspace`` | *not implemented* |
| ``ms``     | *not implemented* |

Token elements are instantiated by passing to the initializer the text as a non
keyword argument  and the attributes as keyword arguments:


```python
x = Identifier('x', mathvariant='bold')
print(x)
```

    <mi mathvariant="bold">x</mi>
    

Note that any object can be passed as the "text" of the token element, provided
that it can be converted to a string.

### Non-token elements

Non-token elements are

  - general layout schemata (see MathML specifications,
  [section 3.1.9.2](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.2)),
  - script and limit schemata (see MathML specifications,
  [section 3.1.9.3](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.3)),
  - tables and matrices (see MathML specifications,
  [section 3.1.9.4](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.4)).

They all derive from the ``Expression`` class, and are instantiated by passing
to the initializer the children expressions as non-keyword arguments, and the
attributes as keyword arguments:


```python
expr = Sup('a', 2, superscriptshift='0.5em')
print(expr)
```

    <msup superscriptshift="0.5em"><mi>a</mi><mn>2</mn></msup>
    

(note that strings and numbers are automatically converted to ``mi`` and ``mn``
children elements, respectively). When relevant, the docstring of the derived
``Element`` lists non-keyword arguments:


```python
print(inspect.getdoc(SubSup))
```

    PyMathML representation of the msubsup element.
    
    See MathML specifications, section 3.4.3.
    
    Usage: SubSup(base, subscript, superscript, **attributes)
    
    which produces the following MathML code:
    
        <msubsup>
            tomathml(base)
            tomathml(subscript)
            tomathml(superscript)
        </msubsup>
    

#### Conversion table for general layout schemata

| MathML       | PyMathML          |
|--------------|-------------------|
| ``mrow``     | ``Row``           |
| ``mfrac``    | ``Frac``          |
| ``msqrt``    | ``Sqrt``          |
| ``mroot``    | ``Root``          |
| ``mstyle``   | ``Style``         |
| ``merror``   | *not implemented* |
| ``mpadded``  | *not implemented* |
| ``mphantom`` | *not implemented* |
| ``mfenced``  | ``Fenced``        |
| ``menclose`` | *not implemented* |

#### Conversion table for script and limit schemata

| MathML            | PyMathML          |
|-------------------|-------------------|
| ``msub``          | ``Sub``           |
| ``msup``          | ``Sup``           |
| ``msubsup``       | ``SubSup``        |
| ``munder``        | ``Under``         |
| ``mover``         | ``Over``          |
| ``munderover``    | ``UnderOver``     |
| ``mmultiscripts`` | *not implemented* |

#### Conversion table for tables and matrices

| MathML          | PyMathML          |
|-----------------|-------------------|
| ``mtable``      | ``Table``         |
| ``mlabeledtr``  | *not implemented* |
| ``mtr``         | ``TableRow``      |
| ``mtd``         | ``TableEntry``    |
| ``maligngroup`` | *not implemented* |
| ``malignmark``  | *not implemented* |

## Building complex expressions with special methods

All special functions of PyMathML objects have been implemented; therefore,
complex expressions can be built very naturally:


```python
f, x = identifiers('f', 'x')

expr = f(x[1], x[2], x[3])**2
```

results in the following MathML code:


```python
print(expr)
```

    <msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup>
    

which renders as ``f(x₁, x₂, x₃)²`` (you need to run the Jupyter notebook to see
the output of the following cell correctly):


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup></math>



#### Conversion table for magic methods

In the table below, ``e``, ``e1`` and ``e2`` are PyMathML expressions, ``me``,
``me1`` and ``me2`` are their translation to MathML.

| PyMathML   | MathML                                                 |
|------------|--------------------------------------------------------|
| ``+e``     | ``<mrow><mo>+</mo>me</mrow>``                          |
| ``-e``     | ``<mrow><mo>-</mo>me</mrow>``                          |
| ``e1+e2``  | ``<mrow>me1<mo>+</mo>me2</mrow>``                      |
| ``e1-e2``  | ``<mrow>me1<mo>-</mo>me2</mrow>``                      |
| ``e1*e2``  | ``<mrow>me1<mo>&it;</mo>me2</mrow>``                   |
| ``e1@e2``  | ``<mrow>me1<mo>⋅</mo>me2</mrow>``                      |
| ``e1**e2`` | ``<msup>me1 me2</msup>``                               |
| ``e1[e2]`` | ``<msub>me1 me2</msub>``                               |
| ``e1(e2)`` | ``<mrow>me1<mo>&af;</mo><mfenced>e2</mfenced></mrow>`` |

#### Caveat

Expressions are *not* automatically parenthetized. For example, the following
snippet


```python
a, b = identifiers('a', 'b')
expr = (a+b)**2
```

results in the following MathML code


```python
print(expr)
```

    <msup><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow><mn>2</mn></msup>
    

which renders as ``a+b²``, not ``(a+b)²``. This is a limitation of this
package, *not a bug*. Indeed, close inspection of the above MathML code reveals
that the expression ``a+b`` is embedded in a ``mrow`` element, so that ``a+b``
is indeed squared.

Until automatic fencing is implemented
(see [issue 1](https://github.com/sbrisard/pymathml/issues/1)),
this is how the above expression should be defined


```python
expr = Fenced(a+b)**2
```

which renders as ``(a+b)²`` as expected:


```python
print(expr)
```

    <msup><mfenced><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow></mfenced><mn>2</mn></msup>
    

## Mathematical operations

PyMathML defines classes that implement unary, binary and n-ary operations as
compound MathML elements.

### Unary operations

Unary operations are derived from the ``UnaryOperation`` class. Examples are
the ``Pos`` and ``Neg`` classes. The single operand is embedded in a ``mrow``
element:


```python
a = Identifier('a')
print('{}\n{}'.format(Pos(a), Neg(a)))
```

    <mrow><mo>+</mo><mi>a</mi></mrow>
    <mrow><mo>-</mo><mi>a</mi></mrow>
    

The above constructs are equivalent to the ``+a`` and ``-a``, respectively:


```python
print('{}\n{}'.format(+a, -a))
```

    <mrow><mo>+</mo><mi>a</mi></mrow>
    <mrow><mo>-</mo><mi>a</mi></mrow>
    

Note that the initializer also accepts attributes, which are passed to the
``mrow`` element:


```python
print(Neg(a, dir='rtl'))
```

    <mrow dir="rtl"><mo>-</mo><mi>a</mi></mrow>
    

New unary operations can be created with the ``unary_operation_type`` function,
like so:


```python
Not = unary_operation_type('Not', '\N{NOT SIGN}')
print(Not(a))
```

    <mrow><mo>¬</mo><mi>a</mi></mrow>
    


```python
print(inspect.getdoc(Not))
```

    PyMathML representation of the ¬ unary operation.
    
    Usage: Not(operand, **attributes)
    
    which produces the following MathML code:
    
        <mrow>
            <mo>¬</mo>
            operand
        </mrow>
    

### Binary operations

Binary operations are derived from the ``BinaryOperation`` class. Currently
implemented binary operations are listed below.

| PyMathML       | Operator |
|----------------|----------|
| Dot            | ⋅        |
| Equals         | =        |
| InvisibleTimes | ⁢         |
| Minus          | -        |
| Plus           | +        |
| Times          | ×        |


The operands are passed to the initializer of the binary operation to be
constructed. They are embedded in a ``mrow`` element.


```python
a, b = identifiers('a', 'b')
print(Minus(a, b))
```

    <mrow><mi>a</mi><mo>-</mo><mi>b</mi></mrow>
    

which is equivalent to ``a-b``:


```python
print(a-b)
```

    <mrow><mi>a</mi><mo>-</mo><mi>b</mi></mrow>
    

Note that the initializer also accepts attributes, which are passed to the
``mrow`` element:


```python
print(Minus(a, b, dir='rtl'))
```

    <mrow dir="rtl"><mi>a</mi><mo>-</mo><mi>b</mi></mrow>
    

Also, assuming associativity, more than two operands can be passed to the
initializer:


```python
c = Identifier('c')
print(Minus(a, b, c))
```

    <mrow><mi>a</mi><mo>-</mo><mi>b</mi><mo>-</mo><mi>c</mi></mrow>
    

which is not strictly equivalent to ``a-b-c`` (the former being embedded in one
single ``mrow`` element):


```python
print(a-b-c)
```

    <mrow><mrow><mi>a</mi><mo>-</mo><mi>b</mi></mrow><mo>-</mo><mi>c</mi></mrow>
    

New binary operations can be created with the ``binary_operation_type``
function, like so:


```python
CircledTimes = binary_operation_type('CircledTimes', '\N{CIRCLED TIMES}')
print(CircledTimes(a, b, c))
```

    <mrow><mi>a</mi><mo>⊗</mo><mi>b</mi><mo>⊗</mo><mi>c</mi></mrow>
    


```python
print(inspect.getdoc(CircledTimes))
```

    PyMathML representation of the ⊗ binary operation.
    
    Usage: CircledTimes(*operands, **attributes)
    
    which produces the following MathML code (associativity is assumed):
    
        <mrow>
            operands[0]
            <mo>⊗</mo>
            operands[1]
            <mo>⊗</mo>
            operands[2]
            ...
        </mrow>
    

### N-ary operations

N-ary operations are derived from the ``NaryOperation`` class. Currently
implemented N-ary operations are listed below.

| PyMathML       | Operator |
|----------------|----------|
| Product        | ∏        |
| Sum            | ∑        |

Three expressions are passed to the initializer of the n-ary operation: the
operand, the ``start`` expression and the ``end`` expression:


```python
a, i, n = identifiers('a', 'i', 'n')
operand = a[i]
start = Equals(i, 0)
end = n
expr = Sum(operand, start, end)
print(expr)
```

    <mrow><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>0</mn></mrow><mi>n</mi></munderover><msub><mi>a</mi><mi>i</mi></msub></mrow>
    

which renders as (only works in the Jupyter notebook)


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mrow><munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>0</mn></mrow><mi>n</mi></munderover><msub><mi>a</mi><mi>i</mi></msub></mrow></math>



Note that, if empty, ``start`` and ``end`` must explicitly be set to ``None``


```python
print(Sum(operand, start, None))
```

    <mrow><munder><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>0</mn></mrow></munder><msub><mi>a</mi><mi>i</mi></msub></mrow>
    


```python
print(Sum(operand, None, end))
```

    <mrow><mover><mo>∑</mo><mi>n</mi></mover><msub><mi>a</mi><mi>i</mi></msub></mrow>
    

Also note that the initializer accepts attributes, which are passed to the
``mrow`` element:


```python
print(Sum(operand, None, None, dir='rtl'))
```

    <mrow dir="rtl"><mo>∑</mo><msub><mi>a</mi><mi>i</mi></msub></mrow>
    

New n-ary operations can be created with the ``nary_operation_type`` function,
like so:


```python
Union = nary_operation_type('Union', '\N{N-ARY UNION}')
print(Union(operand, None, None))
```

    <mrow><mo>⋃</mo><msub><mi>a</mi><mi>i</mi></msub></mrow>
    


```python
print(inspect.getdoc(Union))
```

    PyMathML representation of the ⋃ n-ary operation.
    
    Usage: Union(operand, start, end, **attributes)
    
    If both start and end are not None, the following MathML code is
    produced:
    
        <mrow>
            <munderover>
                <mo>⋃</mo>
                start
                end
            </munderover>
            operand
        </mrow>
    
    If only start is not None, the following MathML code is produced:
    
        <mrow>
            <munder>
                <mo>⋃</mo>
                start
            </munder>
            operand
        </mrow>
    
    Finally, if only end is not None, the following MathML code is
    produced:
    
        <mrow>
            <mover>
                <mo>⋃</mo>
                end
            </mover>
            operand
        </mrow>
    
