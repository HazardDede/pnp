"""Base classes and interfaces for endpoints."""

from fastapi import FastAPI


class Endpoint:
    """Base class for endpoints."""

    def attach(self, fastapi: FastAPI) -> None:
        """Attach this endpoint(s) to the fastapi serving component."""
        raise NotImplementedError()
