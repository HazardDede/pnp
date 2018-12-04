from . import PushBase
from ...utils import is_iterable_but_no_str, parse_duration_literal
from ...validator import Validator


class Echo(PushBase):
    """
    This push simply logs the `payload` via the `logging` module.

    Examples:

        >>> dut = Echo(name="echo_push")
        >>> dut.push("I will be logged")
        'I will be logged'
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        self.logger.info("[{self.name}] Got '{real_payload}' with envelope '{envelope}'".format(**locals()))
        return payload  # Payload as is. With envelope (if any)


class Nop(PushBase):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Nop = No operation OR No push ;-)

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


class Execute(PushBase):
    """
    Executes a command with given arguments in a shell of the operating system.

    Will return the exit code of the command and optionally the output from stdout and stderr.
    """
    def __init__(self, command, args=None, cwd=None, capture=True, timeout="5s", **kwargs):
        super().__init__(**kwargs)
        self._command = str(command) if command else None
        self._args = self._parse_args(args)
        self._cwd = str(cwd) if cwd else None
        Validator.is_directory(allow_none=True, cwd=self._cwd)
        self._capture = bool(capture)
        self._timeout = timeout and parse_duration_literal(timeout)

    def _parse_args(self, val):
        if not val:
            return None
        # Check for list type
        if is_iterable_but_no_str(val):
            return " ".join(val)
        return str(val)

    def _execute(self, args):
        def _output(br):
            return [line.strip('\n\r') for line in br]

        def _command_str():
            if not args:
                return self._command
            return "{self._command} {args}".format(**locals())

        import subprocess
        cmd_str = _command_str()
        self.logger.info("[{self.name}] Running command in shell: {cmd_str}".format(**locals()))
        p = subprocess.Popen(
            args=cmd_str,
            shell=True,
            cwd=self._cwd,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            if self._timeout:
                p.wait(timeout=self._timeout)

            res = dict(return_code=p.returncode)
            if self._capture:
                res['stdout'] = _output(p.stdout)
                res['stderr'] = _output(p.stderr)
            return res
        finally:
            p.stdout.close()
            p.stderr.close()

    def push(self, payload):
        envelope, real_payload = self.envelope_payload(payload)
        args = self._parse_envelope_value('args', envelope)  # Override args via envelope

        return self._execute(args)
