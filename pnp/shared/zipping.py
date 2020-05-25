"""Utility functions related to zipping and archiving."""

import logging
import os
import zipfile
from typing import Optional, Union, Iterable

import pathspec

from pnp import validator
from pnp.utils import is_iterable_but_no_str


_LOGGER = logging.getLogger(__file__)


def zipdir(
    source_dir: str, target_zip: str, ignore: Optional[Union[str, Iterable[str]]] = None
) -> None:
    """Creates a zip file specified by `out_zip`. The source directory is specified
    by `source`. You can optionally specify a gitignore-like ignore list to ignore
    specific items."""
    source_dir = str(source_dir)
    validator.is_directory(source=source_dir)

    target_zip = str(target_zip)

    if ignore is None:
        ignore = []
    if not is_iterable_but_no_str(ignore):
        ignore = [str(ignore)]
    ignore = [str(item) for item in ignore]

    matcher = pathspec.PathSpec.from_lines('gitwildmatch', ignore)
    source_dir = os.path.abspath(source_dir)  # Make relative path -> absolute
    if not source_dir.endswith(os.sep):
        source_dir += os.sep

    _LOGGER.debug("Creating '%s' from '%s'", target_zip, source_dir)
    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipper:
        for root, _, files in os.walk(source_dir):
            for file in files:
                fpath = os.path.join(root, file)
                arcname = fpath.replace(source_dir, '')
                if not matcher.match_file(fpath):  # Apply ignore patterns
                    _LOGGER.debug("Zipping '%s' as '%s", fpath, arcname)
                    zipper.write(fpath, arcname=arcname)
                else:
                    _LOGGER.debug("Ignored '%s'", fpath)


def zipfiles(source_files: Optional[Union[str, Iterable[str]]], target_zip: str) -> None:
    """Zips one or multiple files into a zip file. The target zip file is specified by
    `out_zip`."""
    if not source_files:
        return
    if not is_iterable_but_no_str(source_files):
        source_files = [str(source_files)]
    source_files = [str(fitem) for fitem in source_files]

    _LOGGER.debug("Creating '%s' from %s files", target_zip, len(source_files))
    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipper:
        for fpath in source_files:
            arcname = os.path.basename(fpath)
            _LOGGER.debug("Zipping '%s' as '%s'", fpath, arcname)
            zipper.write(fpath, arcname)


def zipignore(path: str, file_name: str = '.zipignore') -> Iterable[str]:
    """Parses a zipignore file."""
    # Check: Is valid directory
    def filter_(line: str) -> str:
        line = line.strip()  # Remove whitespace characters
        if line.startswith('#'):  # Comment
            return ''  # Will be filtered later
        return line

    zipignore_path = os.path.join(path, file_name)
    if not os.path.isfile(zipignore_path):
        return []  # Shortcircuit -> no file -> no rules

    with open(zipignore_path, 'r') as zih:
        lines = zih.readlines()
    lines.append(file_name)  # Ignore zipignore file name as well

    return filter(
        lambda item: item != '',
        [filter_(line) for line in lines]
    )
