.PHONY: clean-pyc clean-build clean lint test doctest

SOURCE_PATH=./pnp
TEST_PATH=./tests

help:
		@echo "    clean-pyc"
		@echo "        Remove python artifacts."
		@echo "    clean-build"
		@echo "        Remove build artifacts."
		@echo "    lint"
		@echo "        Check style with flake8."
		@echo "    test"
		@echo "        Run py.test"
		@echo "    doctest"
		@echo "        Run doctest"

clean-pyc:
		find . -name '*.pyc' -delete
		find . -name '*.pyo' -delete
		# find . -name '*~' -exec rm --force  {} +

clean-build:
		rm --force --recursive build/
		rm --force --recursive dist/
		rm --force --recursive *.egg-info

clean: clean-pyc

lint:
		flake8 --exclude=.tox --max-line-length 120 $(SOURCE_PATH)

test:
		pytest --verbose --color=yes -s \
			--doctest-modules \
			--cov=$(SOURCE_PATH) --cov-report html --cov-report term $(TEST_PATH) \
			$(SOURCE_PATH)

doctest:
		pytest --verbose --color=yes --doctest-modules $(SOURCE_PATH)
