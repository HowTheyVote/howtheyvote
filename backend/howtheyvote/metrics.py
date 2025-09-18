import datetime
from collections.abc import Iterator

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from sqlalchemy import case, func, select

from .db import Session
from .models import Fragment, Member, PlenarySession, Vote
from .query import member_active_at


class DataCollector(Collector):
    def collect(self) -> Iterator[Metric]:
        yield self.fragments()
        yield self.votes()
        yield self.members()
        yield self.next_session()

    def fragments(self) -> GaugeMetricFamily:
        gauge = GaugeMetricFamily(
            "htv_fragments",
            "Total number of fragments",
            labels=["model", "source_name"],
        )
        query = select(Fragment.model, Fragment.source_name, func.count()).group_by(
            Fragment.model, Fragment.source_name
        )

        for model, source_name, count in Session.execute(query):
            gauge.add_metric(value=count, labels=[model, source_name])

        return gauge

    def votes(self) -> GaugeMetricFamily:
        gauge = GaugeMetricFamily(
            "htv_votes",
            "Total number of votes",
            labels=["year", "is_main"],
        )
        year = func.strftime("%Y", Vote.timestamp)
        query = select(Vote.is_main, year, func.count()).group_by(Vote.is_main, year)

        for is_main, year, count in Session.execute(query):
            gauge.add_metric(value=count, labels=[str(year), str(is_main)])

        return gauge

    def members(self) -> GaugeMetricFamily:
        gauge = GaugeMetricFamily(
            "htv_members", "Total number of members", labels=["country", "active"]
        )
        active = case(
            (member_active_at(datetime.date.today()), True),
            else_=False,
        )
        query = select(
            Member.country,
            active,
            func.count(),
        ).group_by(Member.country, active)

        for country, active, count in Session.execute(query):
            gauge.add_metric(value=count, labels=[country.code, str(active)])

        return gauge

    def next_session(self) -> GaugeMetricFamily:
        today = datetime.date.today()
        gauge = GaugeMetricFamily(
            "htv_next_session_seconds",
            "Seconds until the next plenary session day",
        )
        query = (
            select(PlenarySession)
            .where(func.date(PlenarySession.end_date) >= func.date(today))
            .order_by(PlenarySession.start_date.asc())
            .limit(1)
        )
        next_session = Session.execute(query).scalar()

        if not next_session:
            gauge.add_metric(value=-1, labels=[])
            return gauge

        diff = max(0, (next_session.start_date - today).total_seconds())
        gauge.add_metric(value=diff, labels=[])

        return gauge
