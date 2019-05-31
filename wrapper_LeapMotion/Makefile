all: clean swig py 

swig:
	swig -c++ -python -shadow Leap.i

py: 
	python setup.py build_ext --inplace 

clean: 
	rm -rf build rm *_wrap.* *.o *.so bar.py *.pyc 