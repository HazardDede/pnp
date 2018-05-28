import time

from . import PullBase
from ...utils import make_list


class FileSystemWatcher(PullBase):
    def __init__(self, path, recursive=True, patterns=None, ignore_patterns=None, ignore_directories=False,
                 case_sensitive=False, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self.recursive = recursive
        self.patterns = make_list(patterns)
        self.ignore_patterns = make_list(ignore_patterns)
        self.ignore_directories = ignore_directories
        self.case_sensitive = case_sensitive

    def pull(self):
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler

        notify = self.notify

        class EventHandler(PatternMatchingEventHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def on_any_event(self, event):
                payload = {
                    'operation': event.event_type,
                    'is_directory': getattr(event, 'is_directory', False),
                    'source': getattr(event, 'src_path', None),
                    'destination': getattr(event, 'dest_path', None)
                }
                notify(payload)

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
