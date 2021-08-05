"""Pull: io.FSWatcher"""

from typing import Iterable, Optional, Any, Dict

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from pnp import validator
from pnp.plugins.pull import SyncPull
from pnp.typing import Payload
from pnp.utils import make_list, load_file, FILE_MODES, Debounce, Loggable

__EXTRA__ = 'fswatcher'


# Type aliases
PathLike = str
FilePattern = str


# Constants
EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'
EVENT_TYPES = [EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]

EVENT_DESTINATION_PATH = 'dest_path'
EVENT_IS_DIRECTORY = 'is_directory'
EVENT_SOURCE_PATH = 'src_path'

PAYLOAD_DESTINATION = 'destination'
PAYLOAD_FILE = 'file'
PAYLOAD_IS_DIRECTORY = 'is_directory'
PAYLOAD_OPERATION = 'operation'
PAYLOAD_SOURCE = 'source'


class _EventHandler(PatternMatchingEventHandler, Loggable):  # type: ignore
    def __init__(self, watcher: 'FSWatcher', *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.dispatcher: Dict[str, Debounce] = {}
        self.watcher = watcher

    def _read_file_from_event(self, event: Any) -> Optional[Dict[str, Any]]:
        if (event.event_type != EVENT_TYPE_DELETED
                and not getattr(event, EVENT_IS_DIRECTORY, False)):
            file_name = (
                getattr(event, EVENT_DESTINATION_PATH, None)
                or getattr(event, EVENT_SOURCE_PATH, None)
            )
            if file_name is not None:
                return load_file(file_name, self.watcher.mode, self.watcher.base64)
        return None

    def stop_dispatcher(self) -> None:
        """Stops any pending debounces when the plugin is going to stop."""
        # We cannot alter the dictionary during iteration - so we have to get all relevant
        # debounces beforehand...
        candidates = [debounce for _, debounce in self.dispatcher.items()]
        # ... and then loop it over outside the iterator context
        for debounce in candidates:
            debounce.execute_now()

    def _deferred_notify(self, modified_file: str, payload: Payload) -> None:
        # Let's remove the dispatcher instance - it is done
        self.dispatcher.pop(modified_file, None)
        # trigger the actual notification event
        self.watcher.notify(payload)

    def _notify(self, event: Any, payload: Payload) -> None:
        if event.event_type == EVENT_TYPE_MODIFIED:
            # There might be multiple flushes of a file before it is completely written to
            # disk. Each flush will raise a modified event...
            # Let's wait for more modified events...
            if self.watcher.defer_modified <= 0:
                self.watcher.notify(payload)
            else:
                modified_file = payload[PAYLOAD_SOURCE]
                defer_fun = self.dispatcher.get(modified_file, None)
                if defer_fun is None:
                    defer_fun = Debounce(self._deferred_notify, self.watcher.defer_modified)
                    self.dispatcher[modified_file] = defer_fun
                defer_fun(modified_file, payload)
                self.logger.debug(
                    "Event of modified_file '%s' is deferred for %s",
                    modified_file, self.watcher.defer_modified
                )
        else:
            defer_fun = self.dispatcher.get(payload[PAYLOAD_SOURCE], None)
            # There might be some deferred modified event... Lets check and send it to keep
            # the correct sequence. Assuming the file is closed and finished by now...
            if defer_fun is not None:
                defer_fun.execute_now()
            self.watcher.notify(payload)

    def on_any_event(self, event: Any) -> None:
        """Callback for watchdog."""
        if self.watcher.events is None or event.event_type in self.watcher.events:
            payload = {
                PAYLOAD_OPERATION: event.event_type,
                PAYLOAD_IS_DIRECTORY: getattr(event, EVENT_IS_DIRECTORY, False),
                PAYLOAD_SOURCE: getattr(event, EVENT_SOURCE_PATH, None),
                PAYLOAD_DESTINATION: getattr(event, EVENT_DESTINATION_PATH, None)
            }
            self.logger.info("Got '%s'", payload)
            if self.watcher.load_file:
                file_envelope = self._read_file_from_event(event)
                if file_envelope is not None:
                    payload[PAYLOAD_FILE] = file_envelope

            self._notify(event, payload)


class FSWatcher(SyncPull):
    """
    Watches the given directory for changes like created, moved, modified and deleted files.
    If ignore_directories is set to False, then directories will be reported as well.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#io-fswatcher
    """
    __REPR_FIELDS__ = [
        'base64', 'case_sensitive', 'defer_modified', 'events', 'ignore_directories',
        'ignore_patterns', 'load_file', 'mode', 'path', 'patterns', 'recursive'
    ]

    # pylint: disable=redefined-outer-name
    def __init__(
            self, path: PathLike, recursive: bool = True,
            patterns: Optional[Iterable[FilePattern]] = None,
            ignore_patterns: Optional[Iterable[FilePattern]] = None,
            ignore_directories: bool = False, case_sensitive: bool = False,
            events: Optional[Iterable[str]] = None, load_file: bool = False, mode: str = 'auto',
            base64: bool = False, defer_modified: float = 0.5, **kwargs: Any
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
            validator.subset_of(EVENT_TYPES, events=self.events)
        self.mode = mode
        validator.one_of(FILE_MODES, mode=self.mode)
        self.defer_modified = float(defer_modified)
        if self.defer_modified < 0.0:
            self.defer_modified = 0.5

    def _pull(self) -> None:
        observer = Observer()
        handler = _EventHandler(
            watcher=self,
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=self.ignore_directories,
            case_sensitive=self.case_sensitive
        )
        observer.schedule(handler, self.path, recursive=self.recursive)
        observer.start()

        while not self.stopped:
            self._sleep(1)

        observer.stop()
        handler.stop_dispatcher()
        observer.join()
