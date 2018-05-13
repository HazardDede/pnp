.PHONY: clean-pyc clean-build clean lint test doctest

VERSION=0.1.0
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
		@echo "    rollback"
		@echo "        Rolls back any changes (use for bad version bumps)"

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

rollback:
		git reset --hard HEAD~1                        # rollback the commit
		git tag -d `git describe --tags --abbrev=0`    # delete the tag
