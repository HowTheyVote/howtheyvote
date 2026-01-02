from flask import Blueprint, abort, send_file
from flask.typing import ResponseReturnValue

from ..files import member_photo_path, member_sharepic_path, vote_sharepic_path

CACHE_MAX_AGE = 180 * 24 * 60 * 60
bp = Blueprint("static_api", __name__)


@bp.route("/static/members/<int:member_id>-<int:size>.jpg")
@bp.route("/static/members/<int:member_id>.jpg")
def member_photo(member_id: int, size: int | None = None) -> ResponseReturnValue:
    path = member_photo_path(member_id, size)
    try:
        return send_file(path, max_age=CACHE_MAX_AGE)
    except FileNotFoundError:
        return abort(404)


@bp.route("/static/members/sharepic-<int:member_id>.png")
def member_sharepic(member_id: int) -> ResponseReturnValue:
    path = member_sharepic_path(member_id)
    try:
        return send_file(path, max_age=CACHE_MAX_AGE)
    except FileNotFoundError:
        return abort(404)


@bp.route("/static/votes/sharepic-<int:vote_id>.png")
def vote_sharepic(vote_id: int) -> ResponseReturnValue:
    path = vote_sharepic_path(vote_id)
    try:
        return send_file(path, max_age=CACHE_MAX_AGE)
    except FileNotFoundError:
        return abort(404)
