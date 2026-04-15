# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Prime functions",
    ext_modules=cythonize(
        'prime_functions.pyx',
        compiler_directives={
            'boundscheck': False,
            'wraparound': False,
            'language_level': 3,
        }
    ),
    zip_safe=False,
)