import datetime

from flask import Blueprint, Response, abort, jsonify

from ..db import Session
from ..models import Member
from .serializers import serialize_member

bp = Blueprint("members_api", __name__)


@bp.route("/members/<int:member_id>")
def show(member_id: int) -> Response:
    """
    ---
    get:
        operationId: getMember
        summary: Get member
        tags:
            - Members
        description: |
            Get information about an MEP.
        parameters:
            -
                in: path
                name: member_id
                required: true
                schema:
                    type: string
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Member'
    """
    member = Session.get(Member, member_id)
    today = datetime.date.today()

    if not member:
        return abort(404)

    return jsonify(serialize_member(member, today))
