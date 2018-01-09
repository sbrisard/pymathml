
# PyMathML

PyMathML is a Python package to create MathML expressions programatically.

MathML is extremely verbose; with PyMathML, concise, pythonic expressions are
converted to valid, well-formed MathML code. For example, the following snippet


```python
import inspect

from pymathml import *
from pymathml.utils import *
```


```python
a = Identifier('a')
b = Identifier('b')
expr = a**2+2*a*b+b**2
```

defines the mathematical expression ``a²+2ab+b²``. PyMathML then produces the following MathML code


```python
print(expr)
```

    <mrow><mrow><msup><mi>a</mi><mn>2</mn></msup><mo>+</mo><mrow><mrow><mn>2</mn><mo>⁢</mo><mi>a</mi></mrow><mo>⁢</mo><mi>b</mi></mrow></mrow><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow>
    

PyMathML objects can be displayed in the Jupyter Notebook like so


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mrow><msup><mi>a</mi><mn>2</mn></msup><mo>+</mo><mrow><mrow><mn>2</mn><mo>⁢</mo><mi>a</mi></mrow><mo>⁢</mo><mi>b</mi></mrow></mrow><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow></math>



## Tutorial

The present version of PyMathML is restricted to *Presentation MathML* (see
MathML specifications, [chapter 3](https://www.w3.org/TR/MathML3/chapter3.html)).
All MathML elements are defined as PyMathML objects.

### Creating token elements

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
keyword argument  and the attributes as keyword arguments. For example


```python
x = Identifier('x', mathvariant='bold')
print(x)
```

    <mi mathvariant="bold">x</mi>
    

Note that any object can be passed as the "text" of the token element, provided
that it can be converted to a string.

### Creating non-token elements

Non-token elements are

  - general layout schemata (see MathML specifications,
  [section 3.1.9.2](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.2)),
  - script and limit schemata (see MathML specifications,
  [section 3.1.9.3](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.3)),
  - tables and matrices (see MathML specifications,
  [section 3.1.9.4](https://www.w3.org/TR/MathML3/chapter3.html#id.3.1.9.4)).

They all derive from the ``Expression`` class, and are instantiated by passing
to the initializer the children expressions as non-keyword arguments, and the
attributes as keyword arguments. For example


```python
expr = Sup('a', 2, superscriptshift='0.5em')
print(expr)
```

    <msup superscriptshift="0.5em"><mi>a</mi><mn>2</mn></msup>
    

(note that strings and numbers are automatically converted to ``mi`` and ``mn``
children elements, respectively). When relevant, the docstring of the derived
``Element`` lists non-keyword arguments. For example

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

### Building complex expressions with magic functions

All magic functions of PyMathML objects have been implemented; therefore,
complex expressions can be built very naturally. For example


```python
f = Identifier('f')
x = Identifier('x')

expr = f(x[1], x[2], x[3])**2
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup></math>



which results in the following MathML code


```python
print(expr)
```

    <msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup>
    

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
| ``e1**e2`` | ``<msup>me1 me2</msup>``                               |
| ``e1[e2]`` | ``<msub>me1 me2</msub>``                               |
| ``e1(e2)`` | ``<mrow>me1<mo>&af;</mo><mfenced>e2</mfenced></mrow>`` |

#### Caveat

Expressions are *not* automatically parenthetized. For example, the following
snippet


```python
a = Identifier('a')
b = Identifier('b')
expr = (a+b)**2
```

results in the following MathML code


```python
print(expr)
```

    <msup><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow><mn>2</mn></msup>
    

This is a limitation of this package, *not a bug*. Indeed, close inspection of
the above MathML code reveals that the expression ``a+b`` is enclosed in a
``mrow`` element, so that ``a+b`` is indeed squared. However, this expression
is rendered as follows


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><msup><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow><mn>2</mn></msup></math>



which is not what is expected. Until automatic fencing is implemented (see
[issue 1](https://github.com/sbrisard/pymathml/issues/1)), this is how the
above expression should be defined


```python
expr = Fenced(a+b)**2
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><msup><mfenced><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow></mfenced><mn>2</mn></msup></math>



### Converting PyMathML expressions to MathML

Let us define a PyMathML expression


```python
a, b, c, x = identifiers('a', 'b', 'c', 'x')
expr = a*x**2+b*x+c
```

Then ``str(expr)`` returns its MathML representation


```python
print(expr)
```

    <mrow><mrow><mrow><mi>a</mi><mo>⁢</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>⁢</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow>
    

PyMathML expressions can be displayed (using MathJax) in Jupyter notebooks


```python
expr
```




<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mrow><mrow><mi>a</mi><mo>⁢</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>⁢</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow></math>



``expr.tomathml()`` returns the MathML representation of ``expr`` as an
``Element`` from the ``xml.etree.ElementTree`` module in the
[standard library](https://docs.python.org/3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree)


```python
mml = expr.tomathml()
type(mml)
```




    xml.etree.ElementTree.Element



which can then be converted to XML as follows


```python
import xml.etree.ElementTree as ET

print(ET.tostring(mml, encoding='unicode'))
```

    <mrow><mrow><mrow><mi>a</mi><mo>⁢</mo><msup><mi>x</mi><mn>2</mn></msup></mrow><mo>+</mo><mrow><mi>b</mi><mo>⁢</mo><mi>x</mi></mrow></mrow><mo>+</mo><mi>c</mi></mrow>
    

The function ``tomathml`` promotes its argument to a PyMathML expression, and
calls the ``tomathml()`` method
embeds the expression in a ``math`` element. The optional argu


```python
mml = tomathml('a')
print(ET.tostring(mml, encoding=('unicode')))
```

    <mi>a</mi>
    

If the optional argument ``display`` is specified, the expression is enclosed
in a ``math`` element, with the specified ``display`` attribute


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
    
