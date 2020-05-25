"""Camera related pull plugins."""

import os

from pnp import validator
from pnp.plugins.pull.fs import FileSystemWatcher
from pnp.utils import parse_duration_literal, Debounce, auto_str_ignore


@auto_str_ignore(['_debouncer'])
class MotionEyeWatcher(FileSystemWatcher):
    """
    Watches a MotionEye directory (where the images and the movies get persisted from motioneye)
    to trigger some useful events based on new / modified files.
    The motion event only works, when the camera is configured to persist images / movies
    only when motion is triggered and not 24/7.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/camera.MotionEyeWatcher/index.md

    """

    CONF_EVENT_TYPE_IMAGE = 'image'
    CONF_EVENT_TYPE_MOVIE = 'movie'
    CONF_EVENT_TYPE_MOTION = 'motion'
    CONF_MOTION_ON = 'on'
    CONF_MOTION_OFF = 'off'

    def __init__(self, path, image_ext='jpg', movie_ext='mp4', motion_cool_down='30s', **kwargs):
        if not image_ext and not movie_ext:
            raise TypeError("You have to specify either `image_file_ext`, `movie_file_ext` or both")

        validator.is_instance(str, allow_none=True, image_ext=image_ext)
        self.image_ext = image_ext
        if self.image_ext:
            self.image_ext = self._add_dot_to_ext(self.image_ext)
        validator.is_instance(str, allow_none=True, movie_ext=movie_ext)
        self.movie_ext = movie_ext
        if self.movie_ext:
            self.movie_ext = self._add_dot_to_ext(self.movie_ext)

        self._events = []
        self._patterns = []
        if self.image_ext:
            self._patterns.append('*{}'.format(self.image_ext))
            self._events.append(self.EVENT_TYPE_CREATED)
        if self.movie_ext:
            self._patterns.append('*{}'.format(self.movie_ext))
            self._events.append(self.EVENT_TYPE_MODIFIED)

        super().__init__(
            path=path,
            recursive=True,
            patterns=self._patterns,
            events=self._events,
            load_file=False,
            ignore_directories=True,
            **kwargs
        )

        self.motion_cool_down = parse_duration_literal(motion_cool_down)
        self._debouncer = None

    @staticmethod
    def _add_dot_to_ext(ext):
        return ext if ext.startswith('.') else '.' + ext

    def _motion_off(self, notify_impl):
        self.logger.debug("Send motion 'off' (initial)")
        notify_impl(dict(event=self.CONF_EVENT_TYPE_MOTION, state=self.CONF_MOTION_OFF))
        self._debouncer = None

    def _motion_on(self, notify_impl):
        if self._debouncer is None:
            self.logger.debug("Send motion 'on' (initial)")
            notify_impl(dict(event=self.CONF_EVENT_TYPE_MOTION, state=self.CONF_MOTION_ON))
            self._debouncer = Debounce(self._motion_off, self.motion_cool_down)
        else:
            self.logger.debug("Send motion 'on' (debounced)")
        self._debouncer(notify_impl=notify_impl)

    def notify(self, payload):
        operator = payload.get('operation')
        source = payload.get('source')
        _, ext = os.path.splitext(source)

        if operator == self.EVENT_TYPE_CREATED and ext == self.image_ext:  # This one's an image
            self.logger.debug("Got image '%s' (created)", source)
            self._motion_on(super().notify)
            super().notify(payload=dict(event=self.CONF_EVENT_TYPE_IMAGE, source=source))
        # Creation of movie -> trigger motion
        elif operator == self.EVENT_TYPE_CREATED and ext == self.movie_ext:
            self.logger.debug("Got movie '%s' (created)", source)
            self._motion_on(super().notify)
        elif operator == self.EVENT_TYPE_MODIFIED and ext == self.movie_ext:  # This one's a movie
            self.logger.debug("Got movie '%s' (modified)", source)
            self._motion_on(super().notify)
            super().notify(payload=dict(event=self.CONF_EVENT_TYPE_MOVIE, source=source))
        else:
            self.logger.debug(
                "Got event '%s' with source '%s', but not supported. Ignored...",
                operator, source
            )

    def stop(self):
        if self._debouncer:
            self._debouncer.execute_now()
        super().stop()
