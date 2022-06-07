

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

release:
	bump2version patch --allow-dirty
	# Set next version number
	# Create tags
	git commit --allow-empty -m Release\ `python setup.py --version`
	git tag -a v`python setup.py --version` -m "Version `python setup.py --version`"
	git push --tags

tag:
	git tag -a v`python setup.py --version` -m "Version `python setup.py --version`"
	git push --tags

minor:
	bump2version minor --allow-dirty

upload:
	twine upload dist/*

.PHONY: dist upload test patch minor tag release
