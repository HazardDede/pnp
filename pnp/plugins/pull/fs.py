import time
from threading import Thread

from . import PullBase
from ...utils import make_list, load_file, FILE_MODES
from ...validator import Validator


class FileSystemWatcher(PullBase):
    """
    Watches the given directory for changes like created, moved, modified and deleted files. If `ignore_directories` is
    set to False, then directories will be reported as well.

    Per default will recursively report any file that is touched, changed or deleted in the given path. The
    directory itself or subdirectories will be object to reporting too, if `ignore_directories` is set to False.

    Args:
        path (str): The path to track for events.
        recursive (bool): If set to True, any subfolders of the given path will be tracked too.
        patterns (str or list): Any file pattern (e.g. *.txt or [*.txt, *.md].
        ignore_patterns (str or list): Any patterns to ignore (specify like argument patterns).
        ignore_directories (str): If set to True will send events for directories when file change.
        case_sensitive (bool): If set to True, any pattern is case_sensitive, otherwise it is case insensitive.
        events (str or list): The events to track. One or multiple of 'moved', 'deleted', 'created' and/or 'modified'.
        load_file (bool): If set to True the file will be loaded to the result.
        mode (str): Open mode of the file (only necessary when load_file is True). Can be text, binary or auto
            (guessing).
        base64 (bool): If set to True the loaded file will be converted to base64 (only applicable when
            load_file is True). `mode` will be automatically set to 'binary'.
        defer_modified (float): If set greater than 0, it will defer the sending of modified events for that amount.
            There might be multiple flushes of a file before it is written completely to disk.
            Without defer_modified each flush will raise a modified event.

    Returns:
        The callback `on_payload` will offer a payload that is a dictionary that represents the reported file
        system event. Example ->
            {
                'operation': 'modified',
                'source': '/tmp/abc.txt',
                'is_directory': False,
                'destination': None,  # Only non-None when operation = 'moved'
                'file': {  # Only present when load_file is True
                    'file_name': 'abc.txt',
                    'content': 'foo and bar',
                    'read_mode': 'text',
                    'base64': False
                }
            }

    Example configuration:

        name: watcher
        pull:
          plugin: pnp.plugins.pull.fs.FileSystemWatcher
          args:
            path: '/tmp'
            recursive: True
            patterns: '*.txt'
            ignore_directories: True
            case_sensitive: False
            events: [created, deleted]
            load_file: False
            mode: text
            base64: False
            defer_modified: 0
        push:
            plugin: pnp.plugins.push.simple.Echo
    """

    EVENT_TYPE_MOVED = 'moved'
    EVENT_TYPE_DELETED = 'deleted'
    EVENT_TYPE_CREATED = 'created'
    EVENT_TYPE_MODIFIED = 'modified'
    EVENT_TYPES = [EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]

    def __init__(self, path, recursive=True, patterns=None, ignore_patterns=None, ignore_directories=False,
                 case_sensitive=False, events=None, load_file=False, mode='auto', base64=False, defer_modified=0.5,
                 **kwargs):
        super().__init__(**kwargs)
        self.path = path
        Validator.is_directory(path=self.path)
        self.recursive = bool(recursive)
        self.patterns = make_list(patterns)
        self.ignore_patterns = make_list(ignore_patterns)
        self.ignore_directories = bool(ignore_directories)
        self.case_sensitive = bool(case_sensitive)
        self.load_file = bool(load_file)
        self.base64 = bool(base64)
        self.events = make_list(events)
        Validator.subset_of(self.EVENT_TYPES, allow_none=True, events=self.events)
        self.mode = mode
        Validator.one_of(FILE_MODES, mode=self.mode)
        # TODO: When defer_modified < 0 -> raise ValueError
        # TODO: When defer_modified = 0 -> ignore defer
        self.defer_modified = float(defer_modified)

    def pull(self):
        from watchdog.observers import Observer
        import watchdog.events as wev

        that = self

        class EventHandler(wev.PatternMatchingEventHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.dispatcher = {}

            @staticmethod
            def _read_file_from_event(event):
                if event.event_type != that.EVENT_TYPE_DELETED and not getattr(event, 'is_directory', False):
                    file_name = getattr(event, 'dest_path', None) or getattr(event, 'src_path', None)
                    if file_name is not None:
                        return load_file(file_name, that.mode, that.base64)
                return None

            def _deferred_dispatch(self, modified_file, fingerprint):
                time.sleep(that.defer_modified)
                dispatch_fingerprint, payload = self.dispatcher.get(modified_file, (None, None))
                # If fingerprints do not match, another modified event changed the file... just ignore the change
                if fingerprint == dispatch_fingerprint:
                    # No modifications made. Assuming file is closed and finished
                    that.notify(payload)
                    del self.dispatcher[modified_file]

            def on_any_event(self, event):
                if that.events is None or event.event_type in that.events:
                    payload = {
                        'operation': event.event_type,
                        'is_directory': getattr(event, 'is_directory', False),
                        'source': getattr(event, 'src_path', None),
                        'destination': getattr(event, 'dest_path', None)
                    }
                    that.logger.info("[{that.name}] Got {payload}".format(**locals()))
                    if that.load_file:
                        file_envelope = self._read_file_from_event(event)
                        if file_envelope is not None:
                            payload['file'] = file_envelope

                    if event.event_type == that.EVENT_TYPE_MODIFIED:
                        # There might be multiple flushes of that file before it is written completely to disk
                        # Each flush will raise a modified event... Let's wait for more modified events...
                        modified_file = getattr(event, 'src_path', None)
                        if modified_file is not None:
                            fingerprint = time.time()
                            self.dispatcher[modified_file] = (fingerprint, payload)
                            Thread(target=self._deferred_dispatch, args=(modified_file, fingerprint)).start()
                    else:
                        deferred = self.dispatcher.pop(payload['source'], None)
                        # There might be some deferred modified event... Lets check and send it to keep the correct
                        # sequence. Assuming the file is closed and finished by now...
                        if deferred is not None:
                            _, deferred_payload = deferred
                            that.notify(deferred_payload)
                        that.notify(payload)

        observer = Observer()
        observer.schedule(EventHandler(
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            ignore_directories=self.ignore_directories,
            case_sensitive=self.case_sensitive
        ), self.path, recursive=self.recursive)
        observer.start()

        while not self.stopped:
            time.sleep(1)

        observer.stop()
        observer.join()
