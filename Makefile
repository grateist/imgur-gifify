.PHONY: clean clean_output install run dev lint pip_lock_versions

env:
	python3 -m venv env
	env/bin/python -m pip install -q -U pip setuptools wheel

clean_output:
	rm -rf output

clean: clean_output
	rm -rf env .coverage .pytest_cache .cache coverage.xml pyunit.xml
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

install: env
	env/bin/python -m pip install -q -r requirements-dev.txt

run: env
	env/bin/python main.py

dev: env
	env/bin/python dev.py

lint: env
	env/bin/python -m flake8 gifify *.py

pip_lock_versions: clean env
	env/bin/python -m pip install -q -r requirements-to-freeze.txt
	env/bin/python -m pip freeze > requirements.txt
