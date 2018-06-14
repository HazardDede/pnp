.PHONY: clean-pyc clean-build clean lint test doctest version

VERSION=0.6.1
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
		@echo "    version"
		@echo "        Prints out the current version"

clean-pyc:
		find . -name '*.pyc' -delete
		find . -name '*.pyo' -delete
		# find . -name '*~' -exec rm --force  {} +

clean-build:
		rm --force --recursive build/
		rm --force --recursive dist/
		rm --force --recursive *.egg-info

setup:
		pip install pip --upgrade
		pip install -r requirements.txt --upgrade

clean: clean-pyc

lint:
		flake8 --exclude=.tox --max-line-length 120 --ignore=E722 $(SOURCE_PATH)

test:
		pytest --verbose --color=yes \
			--doctest-modules \
			--cov=$(SOURCE_PATH) --cov-report html --cov-report term $(TEST_PATH) \
			$(SOURCE_PATH)

doctest:
		pytest --verbose --color=yes --doctest-modules $(SOURCE_PATH)

docker:
		docker build -t pnp:$(VERSION) -f Dockerfile .

docker-arm:
		docker build -t pnp:$(VERSION)-arm -f Dockerfile.arm32v7 .

next-version:
		$(eval NEXT_VERSION := $(shell bumpversion --dry-run --allow-dirty --list patch | grep new_version | sed s,"^.*=",,))
		@echo $(NEXT_VERSION)

rollback:
		git reset --hard HEAD~1                        # rollback the commit
		git tag -d `git describe --tags --abbrev=0`    # delete the tag

version:
		@echo $(VERSION)

sdist:
		rm -f dist/*
		python setup.py sdist

release-test: lint test sdist
		twine upload dist/* -r testpypi

release: lint test sdist
		twine upload dist/* -r pypi
