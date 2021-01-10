"""Basic push plugins."""

from functools import partial
from typing import Union, Any

from pnp import validator
from pnp.plugins.push import enveloped, SyncPush, AsyncPush
from pnp.shared.exc import TemplateError
from pnp.utils import parse_duration_literal, make_list, parse_duration_literal_float


class Echo(AsyncPush):
    """
    This push simply logs the `payload` via the `logging` module.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.Echo/index.md

    Examples:

        >>> import asyncio
        >>> loop = asyncio.get_event_loop()
        >>> dut = Echo(name="echo_push")
        >>> loop.run_until_complete(dut.push("I will be logged"))
        'I will be logged'
    """

    @enveloped
    async def _push(self, envelope, payload):  # pylint: disable=arguments-differ
        self.logger.info("Got '%s' with envelope '%s'", payload, envelope)
        # Payload as is. With envelope (if any)
        return {'data': payload, **envelope} if envelope else payload


class Nop(AsyncPush):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Nop = No operation OR No push ;-)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.Nop/index.md

    Examples:

        >>> import asyncio
        >>> loop = asyncio.get_event_loop()
        >>> dut = Nop(name="nop_push")
        >>> loop.run_until_complete(dut.push('I will be returned unaltered'))
        'I will be returned unaltered'
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_payload = None

    async def _push(self, payload):
        self.last_payload = payload
        return payload


class Wait(AsyncPush):
    """
    Performs a sleep operation and wait for some time to go by.
    """
    __REPR_FIELDS__ = ['waiting_interval']

    def __init__(self, wait_for: Union[str, float, int], **kwargs: Any):
        super().__init__(**kwargs)

        self.waiting_interval = parse_duration_literal_float(wait_for)

    async def _push(self, payload):
        import asyncio
        await asyncio.sleep(self.waiting_interval)
        return payload


class Execute(SyncPush):
    """
    Executes a command with given arguments in a shell of the operating system.
    Both `command` and `args` may include placeholders (e.g. `{{placeholder}}`) which are injected
    at runtime by passing the specified payload after selector transformation.

    Will return the exit code of the command and optionally the output from stdout and stderr.
    """
    __REPR_FIELDS__ = ['_args', '_capture', '_command', '_cwd', '_timeout']

    def __init__(self, command, args=None, cwd=None, capture=True, timeout="5s", **kwargs):
        super().__init__(**kwargs)
        self._command = str(command) if command else None
        self._args = self._parse_args(args)
        self._cwd = str(cwd) if cwd else self.base_path
        if self._cwd:
            validator.is_directory(cwd=self._cwd)
        self._capture = bool(capture)
        self._timeout = timeout and parse_duration_literal(timeout)

    @staticmethod
    def _render_jinja_template(template, subs):
        from jinja2 import StrictUndefined
        from jinja2 import Template
        from jinja2.exceptions import UndefinedError
        try:
            tpl = Template(template, undefined=StrictUndefined)
            return tpl.render(**(subs or {}))
        except UndefinedError as exc:
            raise TemplateError('Error when rendering template in TemplatedExecute') from exc

    @staticmethod
    def _parse_args(val):
        args = make_list(val)
        if not args:
            return None
        return [str(arg) for arg in args]

    def _serialize_args(self, transform_fun=None, add_quotes=True):
        def escape_fun(arg):
            return str(arg).replace('"', '\\"')

        def quotes_fun(arg):
            if arg is None or not str(arg) or str(arg).strip() == 'None':
                return ''
            return '"{}"'.format(escape_fun(arg)) if add_quotes else str(arg)

        args = self._args
        if not args:
            return None
        if transform_fun:
            args = [transform_fun(arg) for arg in args]
        # Do argument quoting
        args = [quotes_fun(arg) for arg in args]
        # Remove empty args
        args = [arg for arg in args if arg != '']
        return " ".join(args)

    def _execute(self, command_str):
        def _output(response):
            return [line.strip('\n\r') for line in response]

        import subprocess
        self.logger.info("Running command in shell: %s", command_str)
        proc = subprocess.Popen(
            args=command_str,
            shell=True,
            cwd=self._cwd,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            if self._timeout:
                proc.wait(timeout=int(self._timeout))

            res = dict(return_code=proc.returncode)
            if self._capture:
                res['stdout'] = _output(proc.stdout)
                res['stderr'] = _output(proc.stderr)
            return res
        finally:
            proc.stdout.close()
            proc.stderr.close()

    def _push(self, payload):
        if isinstance(payload, dict):
            subs = payload
        else:
            subs = dict(data=payload, payload=payload)

        command_str = self._render_jinja_template(self._command, subs=subs)
        if self._args:
            args = self._serialize_args(
                transform_fun=partial(self._render_jinja_template, subs=subs),
                add_quotes=True
            )
            command_str = "{command_str} {args}".format(command_str=command_str, args=args)

        return self._execute(command_str)
