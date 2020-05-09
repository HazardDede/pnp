from invoke import task

from tasks.config import (
    SCRIPTS_PATH,
    TEST_PATH,
    VERSION
)

LOCAL_IMAGE_NAME = 'pnp'
LOCAL_IMAGE_TAG = 'local'
PUBLIC_IMAGE_NAME = 'hazard/pnp'


_LOCAL_IMAGE = "{}:{}".format(LOCAL_IMAGE_NAME, LOCAL_IMAGE_TAG)
_PUBLIC_IMAGE = "{}:{}".format(PUBLIC_IMAGE_NAME, VERSION)
_PUBLIC_IMAGE_LATEST = "{}:latest".format(PUBLIC_IMAGE_NAME)


def _dockerfile(arch):
    dockerfile = "Dockerfile"
    if not arch:
        return dockerfile
    return "{}.{}".format(dockerfile, arch.lower())


def _image(base_image, arch):
    if not arch or arch.lower() == 'amd64':
        return base_image
    return "{}-{}".format(base_image, arch.lower())


def _make_image(ctx, arch):
    local_image = _image(_LOCAL_IMAGE, arch)
    dockerfile = _dockerfile(arch)
    print("Building {} with {}".format(local_image, dockerfile))
    ctx.run(
        "docker build -t {local_image} -f {dockerfile} .".format(local_image=local_image, dockerfile=dockerfile)
    )


@task
def config(ctx):
    """Show local and public image names."""
    print("LOCAL IMAGE".ljust(25), _LOCAL_IMAGE)
    print("PUBLIC IMAGE".ljust(25), _PUBLIC_IMAGE)
    print("PUBLIC IMAGE LATEST".ljust(25), _PUBLIC_IMAGE_LATEST)


@task
def make(ctx, arch="amd64"):
    """Builds the docker image for all configured architectures.

    arch: The dockerfile suffix to use. Default is amd64.
    """
    _make_image(ctx, arch)


@task(default=True)
def test(ctx, arch="amd64"):
    """Runs the test suite on a specific docker container.

    arch: The architecture to test. Default is amd64.
    """
    _make_image(ctx, arch)
    local_image = _image(_LOCAL_IMAGE, arch)
    print("Testing image {}".format(local_image))
    ctx.run(
        "{scripts}/test-container {local_image}".format(scripts=SCRIPTS_PATH, local_image=local_image),
        pty=True
    )

    print("Running docker test config.yaml")
    ctx.run(
        "docker run -it --rm "
        "-v {test_path}/docker-test-config.yaml:/config/config.yaml:ro "
        "{local_image}".format(test_path=TEST_PATH, local_image=local_image),
        pty=True
    )


@task
def push(ctx, arch="amd64", latest=False):
    """Pushes the specific docker image to the docker hub. It will not build the docker image - do this before.

    arch: The architecture of the image to push. Default is amd64.
    latest: If set to True the image will be tagged as the latest image on docker hub.
    """
    local_image = _image(_LOCAL_IMAGE, arch)
    public_image = _image(_PUBLIC_IMAGE, arch)

    print("{} -> {}".format(local_image, public_image))
    ctx.run(
        "docker tag {local_image} {public_image} && docker push {public_image}".format(
            local_image=local_image, public_image=public_image
        )
    )
    if latest:
        latest_image = _image(_PUBLIC_IMAGE_LATEST, arch)
        print("{} -> {}".format(public_image, latest_image))
        ctx.run(
            "docker tag {public_image} {latest_image} && docker push {latest_image}".format(
                public_image=public_image, latest_image=latest_image
            )
        )
