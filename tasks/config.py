import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

CONFIGS_PATH = os.path.join(PROJECT_ROOT, 'config')
DOCS_PATH = os.path.join(PROJECT_ROOT, 'docs')
SCRIPTS_PATH = os.path.join(PROJECT_ROOT, 'scripts')
SOURCE_PATH = os.path.join(PROJECT_ROOT, 'pnp')
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')

LOCAL_IMAGE_NAME = 'pnp:local'
PUBLIC_IMAGE_NAME = 'hazard/pnp'
