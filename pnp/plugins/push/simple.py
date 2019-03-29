"""Basic push plugins."""

import warnings
from functools import partial

from . import PushBase, enveloped, parse_envelope, drop_envelope
from ...shared.exc import TemplateError
from ...utils import parse_duration_literal, make_list
from ...validator import Validator


class Echo(PushBase):
    """
    This push simply logs the `payload` via the `logging` module.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.Echo/index.md

    Examples:

        >>> dut = Echo(name="echo_push")
        >>> dut.push("I will be logged")
        'I will be logged'
    """

    def __init__(self, **kwargs):  # pylint: disable=useless-super-delegation
        super().__init__(**kwargs)

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        self.logger.info("[%s] Got '%s' with envelope '%s'", self.name, real_payload, envelope)
        return payload  # Payload as is. With envelope (if any)


class Nop(PushBase):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Nop = No operation OR No push ;-)

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.Nop/index.md

    Examples:

        >>> dut = Nop(name="nop_push")
        >>> dut.push('I will be returned unaltered')
        'I will be returned unaltered'
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_payload = None

    def push(self, payload):
        self.last_payload = payload
        return payload


class TemplatedExecute(PushBase):
    """
    Executes a command with given arguments in a shell of the operating system.
    Both `command` and `args` may include placeholders (e.g. `{{placeholder}}`) which are injected
    at runtime by passing the specified payload after selector transformation.

    Will return the exit code of the command and optionally the output from stdout and stderr.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.TemplatedExecute/index.md
    """
    def __init__(self, command, args=None, cwd=None, capture=True, timeout="5s", **kwargs):
        super().__init__(**kwargs)
        self._command = str(command) if command else None
        self._args = self._parse_args(args)
        self._cwd = str(cwd) if cwd else self.base_path
        Validator.is_directory(allow_none=True, cwd=self._cwd)
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
        print("========>", args)
        return " ".join(args)

    def _execute(self, command_str):
        def _output(response):
            return [line.strip('\n\r') for line in response]

        import subprocess
        self.logger.info("[%s] Running command in shell: %s", self.name, command_str)
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

    def push(self, payload):
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


class Execute(TemplatedExecute):
    """
    Executes a command with given arguments in a shell of the operating system.

    Will return the exit code of the command and optionally the output from stdout and stderr.

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/push/simple.Execute/index.md
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(
            "Plugin `pnp.plugins.push.simple.Execute` is deprecated."
            " Please use `pnp.plugins.push.simple.TemplatedExecute`."
            " In the near future `Execute` will be replaced by `TemplatedExecute`.",
            category=DeprecationWarning,
            stacklevel=2
        )
        warnings.simplefilter('default', DeprecationWarning)

    @enveloped
    @parse_envelope('args')
    @drop_envelope
    def push(self, args, payload):  # pylint: disable=arguments-differ
        command_str = self._command
        if args:
            args = self._serialize_args(
                transform_fun=None,
                add_quotes=False
            )
            command_str = "{command_str} {args}".format(
                command_str=command_str,
                args=args
            )

        return self._execute(command_str)
