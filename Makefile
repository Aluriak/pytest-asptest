t:
	python -m pytest examples --uid-tests-dir examples -vv
tt:
	python -m pytest -p pytest_asptest test --uid-tests-dir examples


install:
	python setup.py install
dev:
	python setup.py develop
