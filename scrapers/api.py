from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from ep_votes.helpers import to_json
from functools import wraps
import datetime
from ep_votes.models import DocReference
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentScraper,
)


def json_response(handler):
    @wraps(handler)
    def wrapper(*args, **kwds):
        res = handler(*args, **kwds)

        if isinstance(res, tuple):
            body, status = res
        else:
            body = res
            status = 200

        return Response(to_json(body), status=status, content_type="application/json")

    return wrapper


def not_found():
    return {"message": "Scraper not found"}, 404


def args_missing(args):
    args = ", ".join(args)
    body = {"message": f"Missing required arguments: {args}"}
    return body, 400


def args(required):
    def call(handler, req):
        args = {}
        missing = [x for x in required if not req.args.get(x)]

        if len(missing) > 0:
            return args_missing(missing)

        for key, type in required.items():
            args[key] = req.args.get(key, type=type)

        return handler(**args)

    def decorator(handler):
        @wraps(handler)
        def wrapper(request):
            return call(handler, request)

        return wrapper

    return decorator


@args({"term": int})
def members(term: int):
    return MembersScraper(term).run()


@args({"web_id": int})
def member_info(web_id: int):
    return MemberInfoScraper(web_id=web_id).run()


@args({"web_id": int, "term": int})
def member_groups(web_id: int, term: int) -> None:
    return MemberGroupsScraper(web_id=web_id, term=term).run()


@args({"date": datetime.date.fromisoformat, "term": int})
def vote_results(date: datetime.date, term: int) -> None:
    return VoteResultsScraper(date=date, term=term).run()


@args({"reference": DocReference.from_str})
def document(reference: DocReference) -> None:
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
def application(req):
    routes = {handler.__name__: handler for handler in ROUTE_HANDLERS}
    route = req.path.removeprefix("/")

    if route not in routes:
        return not_found()

    return routes[route](req)


if __name__ == "__main__":
    run_simple("0.0.0.0", 5000, application)
