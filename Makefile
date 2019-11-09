.PHONY: clean-pyc clean-build clean docs docker docker-arm lint test doctest version

# Setup
VERSION=0.20.0
SOURCE_PATH=./pnp
DOCS_PATH=./docs
CONFIG_PATH=./config
TEST_PATH=./tests
DOCKER_REPO=hazard
IMAGE_NAME=$(DOCKER_REPO)/pnp
LOCAL_IMAGE_NAME=pnp:local
LOCAL_IMAGE_NAME_ARM=pnp:local-arm
FULL_IMAGE_NAME=$(IMAGE_NAME):$(VERSION)
FULL_IMAGE_NAME_ARM=$(IMAGE_NAME):$(VERSION)-arm

# Environment overrides
VERSION_PART?=patch

help:
		@echo "    clean"
		@echo "        Remove python and release artifacts."
		@echo "    setup"
		@echo "        Installs dependencies into the environment"
		@echo "    lint"
		@echo "        Check style with flake8."
		@echo "    test"
		@echo "        Run py.test"
		@echo "    doctest"
		@echo "        Run doctest"
		@echo "    version"
		@echo "        Prints out the current version"
		@echo "    release-test"
		@echo "        Bundles a release and deploys it to test.pypi"
		@echo "    release"
		@echo "        Bundles a release and deploys it to pypi"

clean-pyc:
		find . -name '*.pyc' -delete
		find . -name '*.pyo' -delete
		# find . -name '*~' -exec rm --force  {} +

clean-build:
		rm -rf build/
		rm -rf dist/
		rm -rf *.egg-info
		rm -rf .pytest_cache

clean: clean-pyc clean-build

setup:
		pip install pip --upgrade
		pip install -r requirements.txt --upgrade

docs:
		python ./scripts/process_docs.py

flake8:
		flake8 --exclude=.tox --max-line-length 120 --ignore=E704,E722,E731,W503 $(SOURCE_PATH)

pylint:
		pylint $(SOURCE_PATH)

mypy:
	mypy \
		$(SOURCE_PATH)/logging.py \
		$(SOURCE_PATH)/models.py \
		$(SOURCE_PATH)/selector.py \
		$(SOURCE_PATH)/utils.py \
		$(SOURCE_PATH)/validator.py \
		$(SOURCE_PATH)/engines/*.py \
		$(SOURCE_PATH)/plugins/__init__.py \
		$(SOURCE_PATH)/plugins/pull/__init__.py \
		$(SOURCE_PATH)/plugins/udf/__init__.py \

yamllint:
		yamllint -c .yamllint $(DOCS_PATH) $(CONFIG_PATH)

lint: flake8 pylint yamllint mypy

test-configs:
		python scripts/test_configs.py

pytest:
		pytest --verbose --color=yes \
		    --durations=10 \
			--doctest-modules \
			--cov=$(SOURCE_PATH) --cov-report html --cov-report term $(TEST_PATH) \
			$(SOURCE_PATH)

doctest:
		pytest --verbose --color=yes --doctest-modules $(SOURCE_PATH)

test: test-configs pytest

docker:
	docker build \
		--build-arg INSTALL_DEV_PACKAGES=yes \
		-t $(LOCAL_IMAGE_NAME) \
		-f Dockerfile .
	docker run --rm $(LOCAL_IMAGE_NAME) pytest --durations=10 -vv tests
	docker build \
		--build-arg INSTALL_DEV_PACKAGES=no \
		-t $(LOCAL_IMAGE_NAME) \
		-f Dockerfile .

docker-arm:
	docker build \
		--build-arg INSTALL_DEV_PACKAGES=yes \
		-t $(LOCAL_IMAGE_NAME_ARM) \
		-f Dockerfile.arm32v7 .
	docker run --rm $(LOCAL_IMAGE_NAME_ARM) pytest tests
	docker build \
		--build-arg INSTALL_DEV_PACKAGES=no \
		-t $(LOCAL_IMAGE_NAME_ARM) \
		-f Dockerfile.arm32v7 .

docker-push: docker
	docker tag $(LOCAL_IMAGE_NAME) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	docker tag $(FULL_IMAGE_NAME) $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):latest

docker-push-arm: docker-arm
	docker tag $(LOCAL_IMAGE_NAME_ARM) $(FULL_IMAGE_NAME_ARM)
	docker push $(FULL_IMAGE_NAME_ARM)
	docker tag $(FULL_IMAGE_NAME_ARM) $(IMAGE_NAME):latest-arm
	docker push $(IMAGE_NAME):latest-arm

version:
		@echo $(VERSION)

next-version: lint test-configs test
		$(eval NEXT_VERSION := $(shell bumpversion --dry-run --allow-dirty --list $(VERSION_PART) | grep new_version | sed s,"^.*=",,))
		@echo Next version is $(NEXT_VERSION)
		bumpversion $(VERSION_PART)
		@echo "Review your version changes first"
		@echo "Accept your version: \`make accept-version\`"
		@echo "Revoke your version: \`make revoke-version\`"

accept-version:
		git push && git push --tags

revoke-version:
		git tag -d `git describe --tags --abbrev=0`    # delete the tag
		git reset --hard HEAD~1                        # rollback the commit

sdist:
		rm -f dist/*
		python setup.py sdist

release-test: sdist
		twine upload dist/* -r testpypi

release: sdist
		twine upload dist/* -r pypi
