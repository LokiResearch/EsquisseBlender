#!/usr/bin/env python

# Author: Axel Antoine
# https://axantoine.com

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

"""
setup.py file for SWIG example
"""

from distutils.core import setup, Extension


cgal = Extension('_mycgal',
	sources=['mycgal.i','Point.cpp','Hole.cpp', 'Segment.cpp', 'Region.cpp', 'mycgal.cpp'],
	swig_opts = ['-Wall','-c++'], 
	libraries = ['cgal'],
	library_dirs = ['/usr/local/Cellar/cgal/4.12/lib']
	)

setup (name = 'mycgal',
       version = '0.1',
       author      = "Axel Antoine",
       description = """Swig API generated for python XXXXX""",
       ext_modules = [cgal],
       )