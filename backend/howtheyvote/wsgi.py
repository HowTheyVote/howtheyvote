import time
from typing import Any

import sentry_sdk
from flask import Flask, Response, g, jsonify, request
from flask.typing import ResponseReturnValue
from structlog import get_logger
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .api import bp as api_bp
from .db import Session
from .json import JSONProvider
from .sentry import init_sentry

log = get_logger(__name__)

init_sentry("backend")

app = Flask(__name__, static_folder=None)
app.register_blueprint(api_bp, url_prefix="/api")
app.json = JSONProvider(app)
app.logger = log


# Error handling
def json_error_handler(error: HTTPException) -> ResponseReturnValue:
    code = error.code or 500
    return jsonify(error=str(error)), code


app.register_error_handler(HTTPException, json_error_handler)


# We run the application behind Caddy both in dev and production environments.
# https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#defaults
# mypy complains due to monkey-patching: https://github.com/python/mypy/issues/7347
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore


# SQLAlchemy sessions
@app.teardown_appcontext
def teardown_session(_: Any) -> None:
    Session.remove()


# Request logs/metrics
@app.before_request
def before_request() -> None:
    g.start_time = time.perf_counter()


@app.after_request
def after_request(response: Response) -> Response:
    # perf_counter measures time in seconds
    request_duration = (time.perf_counter() - g.start_time) * 1000

    attributes = {
        "method": request.method,
        "status": response.status_code,
        "route": request.url_rule.endpoint if request.url_rule else None,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8"),
    }

    log.info("Handled request", **attributes, request_duration=round(request_duration))
    sentry_sdk.metrics.count("requests_handled", 1, attributes=attributes)
    sentry_sdk.metrics.distribution(
        "request_duration",
        request_duration,
        attributes=attributes,
        unit="milliseconds",
    )

    return response


# CORS
@app.after_request
def add_cors_header(response: Response) -> Response:
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
