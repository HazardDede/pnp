"""Shared Exceptions."""


class TemplateError(Exception):
    """Is raised when a template cannot be rendered."""


class NoEngineError(Exception):
    """Is raised when no engine is supplied but is needed."""
