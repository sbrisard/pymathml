"""Create MathML expressions programatically with Python.

One notable exception is automatic parenthetizing, which is *not*
implemented. Therefore, this code:

    a = Identifier('a')
    b = Identifier('b')
    (a+b)**2

would be translated to the following MathML

    <mrow><mi>a</mi><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup></mrow>

which in fact renders as

    a+b²
"""

__author__ = 'Sebastien Brisard'
__version__ = '0.0'
__release__ = __version__


from pymathml.core import *
