from zoneinfo import ZoneInfo

from feedgen.feed import FeedGenerator  # type: ignore[import-untyped]
from sqlalchemy import select

from .db import Session
from .files import feed_path
from .models import Vote
from .vote_stats import count_vote_positions


class VotesFeed:
    @staticmethod
    def create() -> None:
        query = (
            select(Vote)
            .where(Vote.is_main.is_(True))
            .order_by(Vote.timestamp.desc())
            .limit(200)
        )
        votes = Session.execute(query).scalars()

        fg = FeedGenerator()
        # General properties of the feed
        fg.id("http://howtheyvote.eu/")
        fg.icon("http://howtheyvote.eu/files/feed_icon.png")
        fg.title("HowTheyVote.eu - Roll-Call Votes in the European Parliament")
        fg.author({"name": "HowTheyVote.eu Team", "email": "mail@howtheyvote.eu"})
        fg.rights("The HowTheyVote.eu database is licensed under the ODbL.")
        fg.subtitle(
            "The European Union is one of the largest democracies in the world."
            "The European Parliament, with its 720 members from the EU’s 27 member states,"
            " represents just over 440 million Europeans. Although the Parliament publishes"  # noqa: E501
            " information such as agendas, minutes, and vote results on its website, it can be"  # noqa: E501
            " quite difficult to find out what MEPs voted on or how a particular vote turned out."  # noqa: E501
            " HowTheyVote.eu compiles voting data from various official sources and allows anyone "  # noqa: E501
            "to search for votes and view the results. This feed provides the 200 newest votes in our database."  # noqa: E501
        )

        for vote in votes:
            fe = fg.add_entry(order="append")
            fe.id("https://howtheyvote.eu/votes/" + str(vote.id))
            fe.title(vote.display_title)
            fe.pubDate(vote.timestamp.replace(tzinfo=ZoneInfo("Europe/Brussels")))
            fe.link(href="https://howtheyvote.eu/votes/" + str(vote.id))
            position_counts = count_vote_positions(vote.member_votes)
            content = (
                f'On {vote.date.strftime("%A, %B %d %Y")} Parliament voted on "'
                f'{vote.display_title}" ({vote.description}). There were {position_counts["FOR"]}'  # noqa: E501
                f" votes in favour, {position_counts['AGAINST']} votes in against,"
                f" and {position_counts['ABSTENTION']} abstentions."
            )
            if vote.result is not None:
                content = content + f" The vote was {vote.result.value}."
            fe.content(content)
        fg.atom_file(feed_path(), pretty=True)
