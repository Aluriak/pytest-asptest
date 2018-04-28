t:
	python -m pytest examples --uid-tests-dir examples -vv
tt:
	python -m pytest -p pytest_asptest test --uid-tests-dir examples


install:
	python setup.py install
dev:
	python setup.py develop
fullrelease:
	fullrelease
install_deps:
	python -c "import configparser; c = configparser.ConfigParser(); c.read('setup.cfg'); print(c['options']['install_requires'])" | xargs pip install -U
