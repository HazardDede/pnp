import glob
import os

import MarkdownPP
from invoke import task


def _process_directory(directory):
    for file_path in glob.iglob(os.path.join(directory, '**/*.mdpp'), recursive=True):
        _process_file(file_path)


def _process_file(file_path):
    modules = MarkdownPP.modules.keys()
    with open(file_path, 'r') as mdpp:
        # Output file takes filename from input file but has .md extension
        with open(os.path.splitext(file_path)[0] + '.md', 'w') as md:
            MarkdownPP.MarkdownPP(input=mdpp, output=md, modules=modules)


@task(default=True)
def docs(ctx):
    """Creates the markdown documentation."""
    _process_directory('docs/plugins/pull')
    _process_directory('docs/plugins/push')
    _process_directory('docs/plugins/udf')
    _process_file('docs/plugins/README.mdpp')
    _process_file('docs/engines/README.mdpp')
    _process_file('docs/README.mdpp')
    _process_file('README.mdpp')
