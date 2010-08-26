RELEASE = 3`rpm --eval %{?dist}`

PY_EXTRA = --install-script greins.spec
REQUIRES = python-routes >= 1.12, gunicorn >= 0.11, gevent >= 0.13.0, python-werkzeug >= 0.6.2
CONFLICTS = dradserver-greins <= 2.1
default:
	python setup.py build

install:
	python setup.py install %(root)

rpm:
	python setup.py bdist_rpm \
    --release="$(RELEASE)" \
    --requires "$(REQUIRES)" \
    --conflicts "$(CONFLICTS)" \
    $(PY_EXTRA)

clean:
	rm -rf MANIFEST
	rm -rf dist
	rm -rf greins.egg-info
	python setup.py clean
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*~" -exec rm -f {} \;
	find . -name "#*#" -exec rm -f {} \;
