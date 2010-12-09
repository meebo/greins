default:
	python setup.py build

install:
	python setup.py install

rpm:
	python setup.py bdist_rpm

clean:
	rm -rf MANIFEST
	rm -rf dist
	rm -rf greins.egg-info
	python setup.py clean
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*~" -exec rm -f {} \;
	find . -name "#*#" -exec rm -f {} \;
