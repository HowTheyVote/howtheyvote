import datetime
from typing import cast

from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue
from sqlalchemy import func, select

from ..db import Session
from ..models import Member, PipelineRun, PlenarySession, Vote
from .serializers import Statistics

bp = Blueprint("stats_api", __name__)


@bp.route("/stats")
def index() -> ResponseReturnValue:
    """
    ---
    get:
        operationId: getStats
        summary: List general stats
        tags:
            - Miscellaneous
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            type: object
                            allOf:
                                - $ref: '#/components/schemas/Statistics'
    """

    query = select(func.count()).select_from(Vote)
    votes_total = cast(int, Session.execute(query).scalar())

    query = select(func.count()).select_from(Member)
    members_total = cast(int, Session.execute(query).scalar())

    start_year = func.min(func.strftime("%Y", PlenarySession.start_date))
    end_year = func.max(func.strftime("%Y", PlenarySession.end_date))
    query = select(end_year - start_year)
    years_total = cast(int, Session.execute(query).scalar())

    query = select(func.max(PipelineRun.finished_at))
    last_update_date = cast(datetime.datetime, Session.execute(query).scalar())

    stats: Statistics = {
        "votes_total": votes_total,
        "members_total": members_total,
        "years_total": years_total,
        "last_update_date": last_update_date,
    }

    return jsonify(stats)
