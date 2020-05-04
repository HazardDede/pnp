from invoke import task

from tasks.config import (
    ARM_SUFFIX_TAG,
    LOCAL_IMAGE_NAME,
    LOCAL_IMAGE_TAG,
    PUBLIC_IMAGE_NAME,
    SCRIPTS_PATH,
    VERSION
)


_LOCAL_IMAGE = "{}:{}".format(LOCAL_IMAGE_NAME, LOCAL_IMAGE_TAG)
_LOCAL_IMAGE_ARM = "{}-{}".format(_LOCAL_IMAGE, ARM_SUFFIX_TAG)

_PUBLIC_IMAGE = "{}:{}".format(PUBLIC_IMAGE_NAME, VERSION)
_PUBLIC_IMAGE_ARM = "{}-{}".format(_PUBLIC_IMAGE, ARM_SUFFIX_TAG)

_PUBLIC_IMAGE_LATEST = "{}:latest".format(PUBLIC_IMAGE_NAME)
_PUBLIC_IMAGE_ARM_LATEST = "{}-{}".format(_PUBLIC_IMAGE_LATEST, ARM_SUFFIX_TAG)


@task
def config(ctx):
    """Show local and public image names."""
    print("LOCAL IMAGE:\t\t", _LOCAL_IMAGE)
    print("LOCAL IMAGE ARM:\t", _LOCAL_IMAGE_ARM)
    print("PUBLIC IMAGE:\t\t", _PUBLIC_IMAGE)
    print("PUBLIC IMAGE ARM:\t", _PUBLIC_IMAGE_ARM)
    print("PUBLIC IMAGE LATEST:\t", _PUBLIC_IMAGE_LATEST)
    print("PUBLIC IMAGE LATEST ARM:", _PUBLIC_IMAGE_ARM_LATEST)


@task
def make_amd64(ctx):
    """Builds the docker image for amd64 as target architecture."""
    ctx.run(
        "docker build -t {local_image} -f Dockerfile .".format(local_image=_LOCAL_IMAGE)
    )


@task
def make_arm(ctx):
    """Builds the docker image for armhf as target architecture."""
    ctx.run(
        "docker build -t {local_image} -f Dockerfile.arm32v7 .".format(local_image=_LOCAL_IMAGE_ARM)
    )


@task(make_amd64, make_arm)
def make(ctx):
    """Builds the docker image for all configured architectures."""


@task(make_amd64)
def test_amd64(ctx):
    """Runs the test-suite on amd64 docker container."""
    ctx.run(
        "{scripts}/test-container {local_image}".format(scripts=SCRIPTS_PATH, local_image=_LOCAL_IMAGE),
        pty=True
    )


@task(make_amd64)
def test_arm(ctx):
    """Runs the test-suite on armhf docker container."""
    ctx.run(
        "{scripts}/test-container {local_image}".format(scripts=SCRIPTS_PATH, local_image=_LOCAL_IMAGE_ARM),
        pty=True
    )


@task(test_amd64, test_arm, default=True)
def test(ctx):
    """Runs the test suite on all available docker containers."""


@task(make_amd64)
def push_amd64(ctx):
    """Push the amd64 docker image to docker hub."""
    ctx.run(
        "docker tag {local_image} {public_image}".format(local_image=_LOCAL_IMAGE, public_image=_PUBLIC_IMAGE)
    )
    ctx.run(
        "docker push {public_image}".format(public_image=_PUBLIC_IMAGE)
    )


@task(make_arm)
def push_arm(ctx):
    """Push the armhf docker image to docker hub."""
    ctx.run(
        "docker tag {local_image} {public_image}".format(local_image=_LOCAL_IMAGE_ARM, public_image=_PUBLIC_IMAGE_ARM)
    )
    ctx.run(
        "docker push {public_image}".format(public_image=_PUBLIC_IMAGE_ARM)
    )


@task(push_amd64, push_arm)
def release(ctx):
    """Mark the last pushed images as latest for amd64 and armhf architectures."""
    ctx.run(
        "docker tag {public_image} {latest_image} && docker push {latest_image}".format(
            public_image=_PUBLIC_IMAGE, latest_image=_PUBLIC_IMAGE_LATEST
        )
    )
    ctx.run(
        "docker tag {public_image} {latest_image} && docker push {latest_image}".format(
            public_image=_PUBLIC_IMAGE_ARM, latest_image=_PUBLIC_IMAGE_ARM_LATEST
        )
    )
