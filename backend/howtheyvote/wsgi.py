from typing import Any

from flask import Flask, Response, jsonify, request, request_started
from flask.typing import ResponseReturnValue
from prometheus_client import PLATFORM_COLLECTOR, CollectorRegistry, make_wsgi_app
from structlog import get_logger
from structlog.contextvars import bind_contextvars, clear_contextvars
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from .api import bp as api_bp
from .db import Session
from .json import JSONProvider
from .metrics import DataCollector
from .sentry import init_sentry

log = get_logger(__name__)

init_sentry()

app = Flask(__name__, static_folder=None)
app.register_blueprint(api_bp, url_prefix="/api")
app.json = JSONProvider(app)
app.logger = log


# Error handling
def json_error_handler(error: HTTPException) -> ResponseReturnValue:
    code = error.code or 500
    return jsonify(error=str(error)), code


app.register_error_handler(HTTPException, json_error_handler)


# Add request info to logs
def bind_request_details(_: Flask) -> None:
    clear_contextvars()
    bind_contextvars(
        path=request.path,
        query_string=request.query_string.decode("utf-8"),
        endpoint=request.url_rule.endpoint if request.url_rule else None,
    )


request_started.connect(bind_request_details, app)


# Prometheus metrics
prometheus_registry = CollectorRegistry()
prometheus_registry.register(PLATFORM_COLLECTOR)
prometheus_registry.register(DataCollector())

prometheus_app = make_wsgi_app(registry=prometheus_registry)
app.wsgi_app = DispatcherMiddleware(  # type: ignore
    app.wsgi_app,
    {
        "/metrics": prometheus_app,
    },
)

# We run the application behind Caddy both in dev and production environments.
# https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#defaults
# mypy complains due to monkey-patching: https://github.com/python/mypy/issues/7347
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore


# SQLAlchemy sessions
@app.teardown_appcontext
def teardown_session(_: Any) -> None:
    Session.remove()


# CORS
@app.after_request
def add_cors_header(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
