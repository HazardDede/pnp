"""Contains metrics related endpoints."""

from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from .base import Endpoint


class PrometheusExporter(Endpoint):
    """Prometheus metrics exporter endpoint."""

    def __init__(self, app_name: str):
        self.app_name = app_name

    def attach(self, fastapi: FastAPI) -> None:
        fastapi.add_middleware(
            PrometheusMiddleware,
            app_name=self.app_name,
            group_paths=True
        )
        fastapi.add_route("/metrics", handle_metrics)
