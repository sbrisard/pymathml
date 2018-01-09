
# PyMathML

PyMathML is a Python package to create MathML expressions programatically.

MathML is extremely verbose; with PyMathML, concise, pythonic expressions are
converted to valid, well-formed MathML code. For example, the following snippet


```python
import inspect
import xml.etree.ElementTree as ET

import pymathml.utils

from pymathml import *
```


```python
a = Identifier('a')
b = Identifier('b')
expr = a**2+2*a*b+b**2
```

defines the mathematical expression ``a²+2ab+b²``. PyMathML then produces the following MathML code


```python
ET.dump(expr.tomathml())
```

    <mrow><mrow><msup><mi>a</mi><mn>2</mn></msup><mo>+</mo><mrow><mrow><mn>2</mn><mo>⁢</mo><mi>a</mi></mrow><mo>⁢</mo><mi>b</mi></mrow></mrow><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow>


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
ET.dump(x.tomathml())
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
ET.dump(expr.tomathml())
```

    <msup superscriptshift="0.5em"><mi>a</mi><mn>2</mn></msup>


(note that strings and numbers are automatically converted to ``mi`` and ``mn``
children elements, respectively). When relevant, the docstring of the derived
``Element`` lists non-keyword arguments. For example


```python
print(inspect.getdoc(SubSup))
```

    PyMathML representation of the ``msubsup`` element.

    See MathML specifications, section 3.4.3.

    Usage: ``SubSup(base, subscript, superscript, **attributes)``

    which produces the following MathML code

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

### Building complex expressions with magic functions

All magic functions of PyMathML objects have been implemented; therefore,
complex expressions can be built very naturally. For example


```python
f = Identifier('f')
x = Identifier('x')
```


```python
expr = f(x[1], x[2], x[3])**2
ET.dump(expr.tomathml())
```

    <msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup>



```python
import IPython.display
```


```python
display(IPython.display.HTML(ET.tostring(pymathml.utils.tomathml(expr, display='block'), encoding='unicode')))
```

<script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=HTMLorMML'></script>

<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><msup><mrow><mi>f</mi><mo>⁡</mo><mfenced><msub><mi>x</mi><mn>1</mn></msub><msub><mi>x</mi><mn>2</mn></msub><msub><mi>x</mi><mn>3</mn></msub></mfenced></mrow><mn>2</mn></msup></math>
