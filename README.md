
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

<math display="block" xmlns="http://www.w3.org/1998/Math/MathML">
<mi>
a
</mi>
</math>
