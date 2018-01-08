import re

from setuptools import setup

with open('pymathml/__init__.py', 'r') as f:
    lines = f.read()
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        lines, re.MULTILINE).group(1)
    description = re.search(r'\"\"\"(.*)',
                            lines, re.MULTILINE).group(1)
    long_description = re.search('\"\"\"(.*)^\"\"\"',
                                 lines, re.MULTILINE | re.DOTALL).group(1)
    author = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]',
                       lines, re.MULTILINE).group(1)

setup(
    name='pymathml',
    version=version,
    description=description,
    long_description=long_description,
    url='',
    author=author,
    author_email='',
    packages=['pymathml'],
    license='BSD-3',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Topic :: Software Development :: Build Tools',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering'],
)
