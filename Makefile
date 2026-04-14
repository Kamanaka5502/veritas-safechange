.PHONY: test build

test:
	pytest -q

build:
	python -m build
