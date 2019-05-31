#!/usr/bin/env python

"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension


LeapPython = Extension('_Leap',
                           sources=['Leap_wrap.cxx'],
                           libraries = ['Leap'],
                           library_dirs = ['.']
                           )

setup (name = 'Leap',
       version = '0.1',
       author      = "Axel Antoine",
       description = """Swig Leap Motion API generated for python XXXXX""",
       ext_modules = [LeapPython],
       )