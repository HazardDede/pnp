"""Contains log related endpoints."""

import logging

from fastapi import FastAPI, Query, HTTPException
from starlette.responses import JSONResponse

from pnp.api.models import EmptyResponse
from .base import Endpoint


class SetLogLevel(Endpoint):
    """Set log level endpoint. Change the logging level during runtime."""

    async def endpoint(
            self,
            level: str = Query(
                ...,
                title="Logging level",
                description="One of DEBUG, INFO, WARNING, ERROR, CRITICAL",
                regex="^DEBUG|INFO|WARNING|ERROR|CRITICAL$"
            )
    ) -> JSONResponse:
        """Change the logging level of the application during runtime.
        Make sure you pass a valid log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
        level = level.upper()
        level_code = logging.getLevelName(level)
        if not isinstance(level_code, int):
            raise HTTPException(
                status_code=422,
                detail="Given log level is not valid. Make sure to pass one of "
                       "DEBUG, INFO, WARNING, ERROR"
            )
        logging.getLogger().setLevel(level_code)
        return EmptyResponse()

    def attach(self, fastapi: FastAPI) -> None:
        fastapi.post(
            path="/loglevel",
            response_class=JSONResponse,
            responses={
                500: {"description": "Internal Server Error"}
            }
        )(self.endpoint)
