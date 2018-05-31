import time

from . import PullBase
from ...utils import make_list, load_file, FILE_MODES
from ...validator import Validator


class FileSystemWatcher(PullBase):
    EVENT_TYPE_MOVED = 'moved'
    EVENT_TYPE_DELETED = 'deleted'
    EVENT_TYPE_CREATED = 'created'
    EVENT_TYPE_MODIFIED = 'modified'
    EVENT_TYPES = [EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]

    def __init__(self, path, recursive=True, patterns=None, ignore_patterns=None, ignore_directories=False,
                 case_sensitive=False, events=None, load_file=False, mode='auto', base64=False, **kwargs):
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
        Validator.one_of(FILE_MODES, mode=mode)

    def pull(self):
        from watchdog.observers import Observer
        import watchdog.events as wev

        that = self

        class EventHandler(wev.PatternMatchingEventHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            @staticmethod
            def _read_file_from_event(event):
                if event.event_type != that.EVENT_TYPE_DELETED and not getattr(event, 'is_directory', False):
                    file_name = getattr(event, 'dest_path', None) or getattr(event, 'src_path', None)
                    if file_name is not None:
                        return load_file(file_name, that.mode, that.base64)
                return None

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
