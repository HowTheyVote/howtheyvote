import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from dotenv import load_dotenv
import datetime
from flask import Flask, Response, request
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


@app.route("/members")
def members() -> Response:
    term = request.args.get("term", type=int)

    if term is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = MembersScraper(term=term)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")


@app.route("/member_info")
def member_info() -> Response:
    web_id = request.args.get("web_id", type=int)

    if web_id is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = MemberInfoScraper(web_id=web_id)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")


@app.route("/member_groups")
def member_groups() -> Response:
    web_id = request.args.get("web_id", type=int)
    term = request.args.get("term", type=int)

    if term is None or web_id is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = MemberGroupsScraper(term=term, web_id=web_id)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")


@app.route("/vote_results")
def vote_results() -> Response:
    term = request.args.get("term", type=int)
    date = request.args.get("date", type=datetime.date.fromisoformat)

    if term is None or date is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = VoteResultsScraper(term=term, date=date)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")


@app.route("/document_info")
def document_info() -> Response:
    type = request.args.get("type", type=lambda x: DocType[x])
    term = request.args.get("term", type=int)
    year = request.args.get("year", type=int)
    number = request.args.get("number", type=int)

    if type is None or term is None or year is None or number is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = DocumentInfoScraper(type=type, term=term, year=year, number=number)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")


@app.route("/procedure")
def procedure() -> Response:
    type = request.args.get("type", type=lambda x: DocType[x])
    term = request.args.get("term", type=int)
    year = request.args.get("year", type=int)
    number = request.args.get("number", type=int)

    if type is None or term is None or year is None or number is None:
        return Response(
            response=to_json({"message": "Missing required paramters"}),
            status=400,
            content_type="application/json",
        )

    scraper = ProcedureScraper(type=type, term=term, year=year, number=number)
    data = scraper.run()

    return Response(response=to_json(data), status=200, content_type="application/json")
