from flask import Blueprint, current_app
from flask.typing import ResponseReturnValue

from .openapi_spec import spec
from .sessions_api import bp as sessions_bp
from .static_api import bp as static_bp
from .stats_api import bp as stats_bp
from .votes_api import bp as votes_bp

bp = Blueprint("api", __name__)

bp.register_blueprint(static_bp)
bp.register_blueprint(votes_bp)
bp.register_blueprint(sessions_bp)
bp.register_blueprint(stats_bp)


@bp.route("/")
def openapi() -> ResponseReturnValue:
    for name, view in current_app.view_functions.items():
        if not name.startswith("api.static."):
            spec.path(view=view)

    return spec.to_dict()
