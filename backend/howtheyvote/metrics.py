import datetime
from collections.abc import Iterator

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from sqlalchemy import case, func, select

from .db import Session
from .models import Fragment, Member, PlenarySession, Vote, VoteGroup
from .query import member_active_at


class DataCollector(Collector):
    def collect(self) -> Iterator[Metric]:
        yield self.fragments()
        yield self.votes()
        yield self.members()
        yield self.next_session()
        yield self.data_issues()

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
            labels=["year", "is_main", "is_featured"],
        )
        year = func.strftime("%Y", Vote.timestamp)
        query = select(Vote.is_main, Vote.is_featured, year, func.count()).group_by(
            Vote.is_main, Vote.is_featured, year
        )

        for is_main, is_featured, year, count in Session.execute(query):
            gauge.add_metric(value=count, labels=[str(year), str(is_main), str(is_featured)])

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

    def data_issues(self) -> GaugeMetricFamily:
        gauge = GaugeMetricFamily(
            "htv_data_issues", "Number of data issues", labels=["type", "month"]
        )

        vote_month = func.strftime("%Y-%m", Vote.timestamp)
        vote_exp = func.json_each(Vote.issues).table_valued("value")
        vote_query = (
            select(vote_exp.c.value, vote_month, func.count())
            .select_from(Vote, vote_exp)
            .group_by(vote_exp.c.value, vote_month)
        )

        vote_group_month = func.strftime("%Y-%m", VoteGroup.date)
        vote_group_exp = func.json_each(VoteGroup.issues).table_valued("value")
        vote_group_query = (
            select(vote_group_exp.c.value, vote_group_month, func.count())
            .select_from(VoteGroup, vote_group_exp)
            .group_by(vote_group_exp.c.value, vote_group_month)
        )

        for type_, month, count in Session.execute(vote_query):
            gauge.add_metric(value=count, labels=[type_, month])

        for type_, month, count in Session.execute(vote_group_query):
            gauge.add_metric(value=count, labels=[type_, month])

        return gauge
