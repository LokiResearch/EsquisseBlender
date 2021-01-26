#!/usr/bin/env python

# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

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