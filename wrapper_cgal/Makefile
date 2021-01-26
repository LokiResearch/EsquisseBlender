# Author: Axel Antoine
# https://axantoine.com
# 01/26/2021

# Loki, Inria project-team with Université de Lille
# within the Joint Research Unit UMR 9189 CNRS-Centrale
# Lille-Université de Lille, CRIStAL.
# https://loki.lille.inria.fr

# LICENCE: Licence.md

all: clean swig py 

swig:
	swig -c++ -python -shadow mycgal.i

py: 
	python setup.py build_ext --inplace 

test: 
	python test.py 

clean: 
	rm -rf build rm *_wrap.* *.o *.so bar.py *.pyc 