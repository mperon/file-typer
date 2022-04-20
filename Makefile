test: patch
	python3 -m pytest

lint:
	pip install pylint
	pylint file_typer

clean:
	rm -rf dist build *.egg-info

dist: patch clean
	python3 -m build .

patch:
	bump2version patch --allow-dirty

tag:
	git tag -a v$(python setup.py --version)

minor:
	bump2version minor --allow-dirty

upload:
	twine upload dist/*

.PHONY: dist upload test patch minor tag
