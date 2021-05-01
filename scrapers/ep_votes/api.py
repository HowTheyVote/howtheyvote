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
    VotingListsScraper,
    DocumentInfoScraper,
    ProcedureScraper,
)

load_dotenv()
sentry_sdk.init(integrations=[FlaskIntegration()])

app = Flask(__name__)

SimpleResponse = Union[Dict, Tuple[Dict, int]]
SimpleHandler = Callable[..., SimpleResponse]


def json_response(handler: SimpleHandler) -> Callable[..., Response]:
    @wraps(handler)
    def wrapped_handler() -> Response:
        res = handler()

        if isinstance(res, tuple):
            body, status = res
        else:
            body = res
            status = 200

        return Response(to_json(body), status=status, content_type="application/json")

    return wrapped_handler


def params(**params: Callable) -> Callable:
    def decorator(handler: SimpleHandler) -> Callable[..., SimpleResponse]:
        @wraps(handler)
        def wrapped_handler() -> SimpleResponse:
            args = request.args
            data = {}

            for key, type in params.items():
                data[key] = args.get(key, type=type)

            missing = [x for x in params if not data[x]]

            if missing:
                message = ", ".join(missing)
                return {"message": f"Missing required parameters: {message}"}, 400

            return handler(**data)

        return wrapped_handler

    return decorator


@app.route("/members")
@json_response
@params(term=int)
def members(term: int) -> SimpleResponse:
    return MembersScraper(term=term).run()


@app.route("/member_info")
@json_response
@params(web_id=int)
def member_info(web_id: int) -> SimpleResponse:
    return MemberInfoScraper(web_id=web_id).run()


@app.route("/member_groups")
@json_response
@params(web_id=int, term=int)
def member_groups(term: int, web_id: int) -> SimpleResponse:
    return MemberGroupsScraper(term=term, web_id=web_id).run()


@app.route("/voting_lists")
@json_response
@params(term=int, date=datetime.date.fromisoformat)
def voting_lists(term: int, date: datetime.date) -> SimpleResponse:
    return VotingListsScraper(term=term, date=date).run()


@app.route("/document_info")
@json_response
@params(type=lambda x: DocType[x], term=int, year=int, number=int)
def document_info(type: DocType, term: int, year: int, number: int) -> SimpleResponse:
    return DocumentInfoScraper(type=type, term=term, year=year, number=number).run()


@app.route("/procedure")
@json_response
@params(type=lambda x: DocType[x], term=int, year=int, number=int)
def procedure(type: DocType, term: int, year: int, number: int) -> SimpleResponse:
    return ProcedureScraper(type=type, term=term, year=year, number=number).run()
