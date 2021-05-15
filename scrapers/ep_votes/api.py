from flask import Flask, Response, request
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
from enum import Enum
import json
from dataclasses import is_dataclass
from datetime import date
import datetime
from functools import wraps
from typing import (
    Callable,
    Dict,
    Tuple,
    Union,
    Any,
    Optional,
)
from .models import Vote, Voting
from .scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VotingListsScraper,
    VoteCollectionsScraper,
)

load_dotenv()
sentry_sdk.init(integrations=[FlaskIntegration()])

app = Flask(__name__)

SimpleResponse = Union[Dict, Tuple[Dict, int]]
SimpleHandler = Callable[..., SimpleResponse]


class EPVotesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, Enum):
            return obj.name

        if isinstance(obj, Vote):
            return dict(obj.__dict__, formatted=obj.formatted)

        if isinstance(obj, Voting):
            return [obj.name, obj.position]

        if is_dataclass(obj):
            return obj.__dict__

        return super(EPVotesEncoder, self).default(obj)


def to_json(data: Any, indent: Optional[int] = None) -> str:
    return json.dumps(data, cls=EPVotesEncoder, indent=indent)


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


@app.route("/vote_collections")
@json_response
@params(term=int, date=datetime.date.fromisoformat)
def vote_collections(term: int, date: datetime.date) -> SimpleResponse:
    return VoteCollectionsScraper(term=term, date=date).run()
