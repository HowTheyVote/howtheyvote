import datetime

from flask import Blueprint, abort, jsonify
from flask.typing import ResponseReturnValue

from ..db import Session
from ..models import Member
from .serializers import serialize_group, serialize_member, serialize_national_party

bp = Blueprint("members_api", __name__)


@bp.route("/members/<int:member_id>")
def show(member_id: int) -> ResponseReturnValue:
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

    if not member or not member.group_memberships:
        return abort(404)

    group = member.group_at(today) or member.group_memberships[-1].group
    national_party = member.national_party_at(today)

    return jsonify(
        {
            **serialize_member(member, today),
            "group": serialize_group(group),
            "national_party": serialize_national_party(national_party)
            if national_party is not None
            else None,
        }
    )
