from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import os
from typing import Callable, Dict, Tuple, List, Union, Any
from functools import wraps
import datetime
from .helpers import to_json, removeprefix
from .models import Member, DocReference, GroupMembership, Vote, Doc
from .scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentScraper,
)


SimpleResponse = Union[Dict, Tuple[Dict, int]]
SimpleHandler = Callable[..., SimpleResponse]
Handler = Callable[..., Response]


def json_response(handler: SimpleHandler) -> Handler:
    @wraps(handler)
    def wrapper(*args: Any, **kwds: Any) -> Response:
        res = handler(*args, **kwds)

        if isinstance(res, tuple):
            body, status = res
        else:
            body = res
            status = 200

        return Response(to_json(body), status=status, content_type="application/json")

    return wrapper


def not_found() -> SimpleResponse:
    return {"message": "Scraper not found"}, 404


def args_missing(args: List[str]) -> SimpleResponse:
    missing = ", ".join(args)
    body = {"message": f"Missing required arguments: {missing}"}
    return body, 400


def args(required: Dict[str, Callable]) -> Callable[..., SimpleHandler]:
    def call(handler: SimpleHandler, req: Request) -> SimpleResponse:
        args = {}
        missing = [x for x in required if not req.args.get(x)]

        if len(missing) > 0:
            return args_missing(missing)

        for key, type in required.items():
            args[key] = req.args.get(key, type=type)

        return handler(**args)

    def decorator(handler: SimpleHandler) -> SimpleHandler:
        @wraps(handler)
        def wrapper(request: Request) -> SimpleResponse:
            return call(handler, request)

        return wrapper

    return decorator


@args({"term": int})
def members(term: int) -> List[Member]:
    return MembersScraper(term).run()


@args({"web_id": int})
def member_info(web_id: int) -> Member:
    return MemberInfoScraper(web_id=web_id).run()


@args({"web_id": int, "term": int})
def member_groups(web_id: int, term: int) -> List[GroupMembership]:
    return MemberGroupsScraper(web_id=web_id, term=term).run()


@args({"date": datetime.date.fromisoformat, "term": int})
def vote_results(date: datetime.date, term: int) -> List[Vote]:
    return VoteResultsScraper(date=date, term=term).run()


@args({"reference": DocReference.from_str})
def document(reference: DocReference) -> Doc:
    return DocumentScraper(reference=reference).run()


ROUTE_HANDLERS = [
    members,
    member_info,
    member_groups,
    vote_results,
    document,
]


@Request.application
@json_response
def application(req: Request) -> SimpleResponse:
    routes = {handler.__name__: handler for handler in ROUTE_HANDLERS}
    route = removeprefix(req.path, "/")

    if route not in routes:
        return not_found()

    return routes[route](req)


if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", 80))
    run_simple(host, port, application)
