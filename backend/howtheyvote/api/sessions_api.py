import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseValue

from ..models import PlenarySession
from .query import DatabaseQuery, Order
from .serializers import (
    PlenarySessionDict,
    PlenarySessionsQueryResponseDict,
    serialize_plenary_session,
)

bp = Blueprint("sessions_api", __name__)


@bp.route("/sessions")
def index() -> ResponseValue:
    """
    ---
    get:
        operationId: getSessions
        summary: List sessions
        tags:
            - Plenary sessions
        parameters:
            -   in: query
                name: status
                schema:
                    type: string
                    enum:
                        - current
                        - past
                        - upcoming
            -   in: query
                name: page
                description: Results page
                schema:
                    type: integer
                    default: 1
            -   in: query
                name: page_size
                description: Number of results per page
                schema:
                    type: integer
                    default: 20
            -   in: query
                name: sort_order
                description: Sort order
                schema:
                    type: string
                    default: asc
                    enum:
                        - asc
                        - desc
        responses:
            '200':
                description: Ok
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/PlenarySessionsQueryResponse'
    """

    today = datetime.date.today()
    status = request.args.get("status", None)

    query = DatabaseQuery(PlenarySession).sort("start_date")
    query = query.page(request.args.get("page", type=int))
    query = query.page_size(request.args.get("page_size", type=int))

    if request.args.get("sort_order") == "desc":
        query = query.sort("start_date", Order.DESC)
    else:
        query = query.sort("start_date", Order.ASC)

    if status == "current":
        query = query.filter("start_date", "<=", today)
        query = query.filter("end_date", ">=", today)

    if status == "past":
        query = query.filter("end_date", "<", today)

    if status == "upcoming":
        query = query.filter("start_date", ">", today)

    response = query.handle()
    results: list[PlenarySessionDict] = [
        serialize_plenary_session(ps) for ps in response["results"]
    ]

    data: PlenarySessionsQueryResponseDict = {
        **response,
        "results": results,
    }

    return jsonify(data)
