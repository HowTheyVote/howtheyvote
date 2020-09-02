from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
import os
from typing import (
    Callable,
    Dict,
    Tuple,
    List,
    Union,
    Any,
    Type,
)
from typing_extensions import TypedDict
from functools import wraps
import datetime
from .helpers import to_json, removeprefix, removesuffix
from .models import DocReference
from .scrapers import (
    Scraper,
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
    def wrapper(request: Request, *args: Any, **kwds: Any) -> Response:
        res = handler(request, *args, **kwds)
        indent = 2 if "pretty" in request.args else None

        if isinstance(res, tuple):
            body, status = res
        else:
            body = res
            status = 200

        return Response(
            to_json(body, indent=indent), status=status, content_type="application/json"
        )

    return wrapper


def not_found() -> SimpleResponse:
    return {"message": "Scraper not found"}, 404


def params_missing(params: List[str]) -> SimpleResponse:
    missing = ", ".join(params)
    body = {"message": f"Missing required arguments: {missing}"}
    return body, 400


def require_params(required: Dict[str, Callable]) -> Callable[..., SimpleHandler]:
    def call(handler: SimpleHandler, req: Request) -> SimpleResponse:
        params = {}
        missing = [x for x in required if not req.args.get(x)]

        if len(missing) > 0:
            return params_missing(missing)

        for key, type in required.items():
            params[key] = req.args.get(key, type=type)

        return handler(**params)

    def decorator(handler: SimpleHandler) -> SimpleHandler:
        @wraps(handler)
        def wrapper(request: Request) -> SimpleResponse:
            return call(handler, request)

        return wrapper

    return decorator


Route = TypedDict(
    "Route",
    {
        "scraper": Type[Scraper],
        "params": Dict[str, Callable[..., Any]],
    },
)

ROUTES: Dict[str, Route] = {
    "members": {
        "scraper": MembersScraper,
        "params": {"term": int},
    },
    "member_info": {
        "scraper": MemberInfoScraper,
        "params": {"web_id": int},
    },
    "member_groups": {
        "scraper": MemberGroupsScraper,
        "params": {"web_id": int, "term": int},
    },
    "vote_results": {
        "scraper": VoteResultsScraper,
        "params": {"date": datetime.date.fromisoformat, "term": int},
    },
    "documents": {
        "scraper": DocumentScraper,
        "params": {"reference": DocReference.from_str},
    },
}


@Request.application
@json_response
def application(req: Request) -> SimpleResponse:
    path = removesuffix(removeprefix(req.path, "/"), "/")

    if path not in ROUTES:
        return not_found()

    scraper = ROUTES[path]["scraper"]
    params = ROUTES[path]["params"]
    args_decorator = require_params(params)

    def handler(**args: Any) -> SimpleResponse:
        return scraper(**args).run()

    return args_decorator(handler)(req)


if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", 80))
    run_simple(host, port, application)
