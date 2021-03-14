from flask import Flask, Response, request
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
import datetime
from functools import wraps
from typing import (
    Callable,
    Dict,
    Tuple,
    Union,
)
from .helpers import to_json
from .models import DocType
from .scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentInfoScraper,
    ProcedureScraper,
)

load_dotenv()
sentry_sdk.init(integrations=[FlaskIntegration()])

app = Flask(__name__)

SimpleResponse = Union[Dict, Tuple[Dict, int]]
SimpleHandler = Callable[..., SimpleResponse]
Handler = Callable[..., Response]


def json_response(handler: SimpleHandler) -> Handler:
    @wraps(handler)
    def wrapper() -> Response:
        res = handler()

        if isinstance(res, tuple):
            body, status = res
        else:
            body = res
            status = 200

        return Response(to_json(body), status=status, content_type="application/json")

    return wrapper


@app.route("/members")
@json_response
def members() -> SimpleResponse:
    term = request.args.get("term", type=int)

    if term is None:
        return {"message": "Missing required paramters"}, 400

    return MembersScraper(term=term).run()


@app.route("/member_info")
@json_response
def member_info() -> SimpleResponse:
    web_id = request.args.get("web_id", type=int)

    if web_id is None:
        return {"message": "Missing required paramters"}, 400

    return MemberInfoScraper(web_id=web_id).run()


@app.route("/member_groups")
@json_response
def member_groups() -> SimpleResponse:
    web_id = request.args.get("web_id", type=int)
    term = request.args.get("term", type=int)

    if term is None or web_id is None:
        return {"message": "Missing required paramters"}, 400

    return MemberGroupsScraper(term=term, web_id=web_id).run()


@app.route("/vote_results")
@json_response
def vote_results() -> SimpleResponse:
    term = request.args.get("term", type=int)
    date = request.args.get("date", type=datetime.date.fromisoformat)

    if term is None or date is None:
        return {"message": "Missing rrequired paramters"}, 400

    return VoteResultsScraper(term=term, date=date).run()


@app.route("/document_info")
@json_response
def document_info() -> SimpleResponse:
    type = request.args.get("type", type=lambda x: DocType[x])
    term = request.args.get("term", type=int)
    year = request.args.get("year", type=int)
    number = request.args.get("number", type=int)

    if type is None or term is None or year is None or number is None:
        return {"message": "Missing rrequired paramters"}, 400

    return DocumentInfoScraper(type=type, term=term, year=year, number=number).run()


@app.route("/procedure")
@json_response
def procedure() -> SimpleResponse:
    type = request.args.get("type", type=lambda x: DocType[x])
    term = request.args.get("term", type=int)
    year = request.args.get("year", type=int)
    number = request.args.get("number", type=int)

    if type is None or term is None or year is None or number is None:
        return {"message": "Missing required paramters"}, 400

    return ProcedureScraper(type=type, term=term, year=year, number=number).run()
