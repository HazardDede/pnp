import os

# VERSION
VERSION = "0.22.0"

# PROJECT ROOT
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# PATH STUFF
CONFIGS_PATH = os.path.join(PROJECT_ROOT, 'config')
DOCS_PATH = os.path.join(PROJECT_ROOT, 'docs')
SCRIPTS_PATH = os.path.join(PROJECT_ROOT, 'scripts')
SOURCE_PATH = os.path.join(PROJECT_ROOT, 'pnp')
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')

# DOCKER STUFF
LOCAL_IMAGE_NAME = 'pnp'
LOCAL_IMAGE_TAG = 'local'
ARM_SUFFIX_TAG = 'arm'
PUBLIC_IMAGE_NAME = 'hazard/pnp'
