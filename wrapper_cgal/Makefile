all: clean swig py 

swig:
	swig -c++ -python -shadow mycgal.i

py: 
	python setup.py build_ext --inplace 

test: 
	python test.py 

clean: 
	rm -rf build rm *_wrap.* *.o *.so bar.py *.pyc 