"""File system related plugins."""

import os
import time

from pnp import validator
from pnp.plugins import load_optional_module, PluginStoppedError
from pnp.plugins.pull import PullBase, Polling
from pnp.utils import make_list, load_file, FILE_MODES, Debounce


class FileSystemWatcher(PullBase):
    """
    Watches the given directory for changes like created, moved, modified and deleted files.
    If ignore_directories is set to False, then directories will be reported as well.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/fs.FileSystemWatcher/index.md
    """

    EXTRA = 'fswatcher'
    EVENT_TYPE_MOVED = 'moved'
    EVENT_TYPE_DELETED = 'deleted'
    EVENT_TYPE_CREATED = 'created'
    EVENT_TYPE_MODIFIED = 'modified'
    EVENT_TYPES = [EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]

    # pylint: disable=redefined-outer-name
    def __init__(
        self, path, recursive=True, patterns=None, ignore_patterns=None,
        ignore_directories=False, case_sensitive=False, events=None, load_file=False,
        mode='auto', base64=False, defer_modified=0.5, **kwargs
    ):
        super().__init__(**kwargs)
        self.path = path
        validator.is_directory(path=self.path)
        self.recursive = bool(recursive)
        self.patterns = make_list(patterns)
        self.ignore_patterns = make_list(ignore_patterns)
        self.ignore_directories = bool(ignore_directories)
        self.case_sensitive = bool(case_sensitive)
        self.load_file = bool(load_file)
        self.base64 = bool(base64)
        self.events = make_list(events)
        if self.events:
            validator.subset_of(self.EVENT_TYPES, events=self.events)
        self.mode = mode
        validator.one_of(FILE_MODES, mode=self.mode)
        self.defer_modified = float(defer_modified)
        if self.defer_modified < 0.0:
            self.defer_modified = 0.5

    def pull(self):
        wdog = load_optional_module('watchdog.observers', self.EXTRA)
        wev = load_optional_module('watchdog.events', self.EXTRA)

        that = self

        class _EventHandler(wev.PatternMatchingEventHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.dispatcher = {}

            @staticmethod
            def _read_file_from_event(event):
                if (event.event_type != that.EVENT_TYPE_DELETED
                        and not getattr(event, 'is_directory', False)):
                    file_name = (
                        getattr(event, 'dest_path', None)
                        or getattr(event, 'src_path', None)
                    )
                    if file_name is not None:
                        return load_file(file_name, that.mode, that.base64)
                return None

            def stop_dispatcher(self):
                """Stops any pending debounces when the plugin is going to stop."""
                # We cannot alter the dictionary during iteration - so we have to get all relevant
                # debounces beforehand...
                candidates = [debounce for _, debounce in self.dispatcher.items()]
                # ... and then loop it over outside the iterator context
                for debounce in candidates:
                    debounce.execute_now()

            def _deferred_notify(self, modified_file, payload):
                # Let's remove the dispatcher instance - it is done
                self.dispatcher.pop(modified_file, None)
                # trigger the actual notification event
                that.notify(payload)

            def _notify(self, event, payload):
                if event.event_type == that.EVENT_TYPE_MODIFIED:
                    # There might be multiple flushes of a file before it is completely written to
                    # disk. Each flush will raise a modified event...
                    # Let's wait for more modified events...
                    if that.defer_modified <= 0:
                        that.notify(payload)
                    else:
                        modified_file = payload['source']
                        defer_fun = self.dispatcher.get(modified_file, None)
                        if defer_fun is None:
                            defer_fun = Debounce(self._deferred_notify, that.defer_modified)
                            self.dispatcher[modified_file] = defer_fun
                        defer_fun(modified_file, payload)
                        that.logger.debug(
                            "Event of modified_file '%s' is deferred for %s",
                            modified_file, that.defer_modified
                        )
                else:
                    defer_fun = self.dispatcher.get(payload['source'], None)
                    # There might be some deferred modified event... Lets check and send it to keep
                    # the correct sequence. Assuming the file is closed and finished by now...
                    if defer_fun is not None:
                        defer_fun.execute_now()
                    that.notify(payload)

            def on_any_event(self, event):
                """Callback for watchdog."""
                if that.events is None or event.event_type in that.events:
                    payload = {
                        'operation': event.event_type,
                        'is_directory': getattr(event, 'is_directory', False),
                        'source': getattr(event, 'src_path', None),
                        'destination': getattr(event, 'dest_path', None)
                    }
                    that.logger.info("Got '%s'", payload)
                    if that.load_file:
                        file_envelope = self._read_file_from_event(event)
                        if file_envelope is not None:
                            payload['file'] = file_envelope

                    self._notify(event, payload)

        observer = wdog.Observer()
        handler = _EventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=self.ignore_directories,
            case_sensitive=self.case_sensitive
        )
        observer.schedule(handler, self.path, recursive=self.recursive)
        observer.start()

        while not self.stopped:
            time.sleep(1)

        observer.stop()
        handler.stop_dispatcher()
        observer.join()


class Size(Polling):
    """
    Periodically determines the size of the specified files or directories in bytes.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/fs.FileSize/index.md
    """

    def __init__(self, paths, fail_on_error=True, **kwargs):
        super().__init__(**kwargs)
        if isinstance(paths, dict):
            self.file_paths = paths  # alias -> file path mapping
        else:
            # No explicit alias: Use the basename of the file
            self.file_paths = {os.path.basename(str(fp)): str(fp) for fp in make_list(paths)}
        self.fail_on_error = bool(fail_on_error)

    @staticmethod
    def _file_size(path):
        return os.path.getsize(path)

    def _dir_size(self, path):
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                fp = os.path.join(dirpath, fname)
                try:
                    total_size += self._file_size(os.path.realpath(fp))
                except FileNotFoundError:
                    self.logger.warning(
                        "File %s does not exists when calculating the directory size", fp)
                finally:
                    if self.stopped:
                        raise PluginStoppedError(
                            "Aborted calculation of directory size, due to stop of plugin")

        return total_size

    def _size(self, path):
        try:
            if os.path.isdir(path):
                return self._dir_size(path)
            return self._file_size(path)
        except (FileNotFoundError, NotADirectoryError):
            if self.fail_on_error:
                raise
            return None

    def poll(self):
        return {
            alias: self._size(fp)
            for alias, fp in self.file_paths.items()
        }
