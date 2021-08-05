"""Push: simple.Execute."""

import subprocess
from functools import partial
from typing import Optional, List, Union, Any, Dict, Callable, IO

from jinja2 import StrictUndefined, Template
from jinja2.exceptions import UndefinedError
from typeguard import typechecked

from pnp import validator
from pnp.exc import TemplateError
from pnp.plugins.push import SyncPush
from pnp.typing import DurationLiteral, Payload
from pnp.utils import parse_duration_literal, make_list


class Execute(SyncPush):
    """
    Executes a command with given arguments in a shell of the operating system.
    Both `command` and `args` may include placeholders (e.g. `{{placeholder}}`) which are injected
    at runtime by passing the specified payload after selector transformation.

    Will return the exit code of the command and optionally the output from stdout and stderr.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#simple-execute
    """
    __REPR_FIELDS__ = ['args', 'capture', 'command', 'cwd', 'timeout']

    @typechecked
    def __init__(
            self, command: str, args: Optional[Union[str, List[str]]] = None,
            cwd: Optional[str] = None, capture: bool = True,
            timeout: Optional[DurationLiteral] = "5s", **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.command = str(command)
        self.args = self._parse_args(args)
        self.cwd = str(cwd) if cwd else self.base_path
        if self.cwd:
            validator.is_directory(cwd=self.cwd)
        self.capture = bool(capture)
        self.timeout = timeout and parse_duration_literal(timeout)

    @staticmethod
    def _render_jinja_template(template: str, subs: Dict[str, str]) -> str:
        try:
            tpl = Template(template, undefined=StrictUndefined)
            return tpl.render(**(subs or {}))
        except UndefinedError as exc:
            raise TemplateError('Error when rendering template in TemplatedExecute') from exc

    @staticmethod
    def _parse_args(val: Any) -> Optional[List[str]]:
        args = make_list(val)
        if not args:
            return None
        return [str(arg) for arg in args]

    def _serialize_args(
            self, transform_fun: Optional[Callable[[str], str]] = None, add_quotes: bool = True
    ) -> Optional[str]:
        def escape_fun(arg: Any) -> str:
            return str(arg).replace('"', '\\"')

        def quotes_fun(arg: Any) -> str:
            if arg is None or not str(arg) or str(arg).strip() == 'None':
                return ''
            return '"{}"'.format(escape_fun(arg)) if add_quotes else str(arg)

        args = self.args
        if not args:
            return None
        if transform_fun:
            args = [transform_fun(arg) for arg in args]
        # Do argument quoting
        args = [quotes_fun(arg) for arg in args]
        # Remove empty args
        args = [arg for arg in args if arg != '']
        return " ".join(args)

    def _execute(self, command_str: str) -> Dict[str, Any]:
        def _output(response: Optional[IO[str]]) -> List[str]:
            if not response:
                return []
            return [line.strip('\n\r') for line in response]

        self.logger.info("Running command in shell: %s", command_str)
        proc = subprocess.Popen(
            args=command_str,
            shell=True,
            cwd=self.cwd,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            if self.timeout:
                proc.wait(timeout=int(self.timeout))

            res: Dict[str, Any] = dict(return_code=proc.returncode)
            if self.capture:
                res['stdout'] = _output(proc.stdout)
                res['stderr'] = _output(proc.stderr)
            return res
        finally:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()

    def _push(self, payload: Payload) -> Payload:
        if isinstance(payload, dict):
            subs = payload
        else:
            subs = dict(data=payload, payload=payload)

        command_str = self._render_jinja_template(self.command, subs=subs)
        if self.args:
            args = self._serialize_args(
                transform_fun=partial(self._render_jinja_template, subs=subs),
                add_quotes=True
            )
            command_str = "{command_str} {args}".format(command_str=command_str, args=args)

        return self._execute(command_str)
