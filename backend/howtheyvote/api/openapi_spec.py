from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin

from .. import config
from .openapi_helpers import get_schema, normalize_schema_name
from .serializers import (
    AmendmentAuthorDict,
    BaseVoteDict,
    BaseVoteWithMemberPositionDict,
    CommitteeDict,
    CountryDict,
    EurovocConceptDict,
    FacetOptionDict,
    GroupDict,
    LinkDict,
    MemberDict,
    MemberVoteDict,
    MemberVotesQueryResponseDict,
    OEILSubjectDict,
    PlenarySessionDict,
    PlenarySessionsQueryResponseDict,
    ProcedureDict,
    QueryResponseDict,
    QueryResponseWithFacetsDict,
    RelatedVoteDict,
    SourceDict,
    Statistics,
    VoteDict,
    VotePositionCountsDict,
    VotesQueryResponseDict,
    VoteStatsByCountryDict,
    VoteStatsByGroupDict,
    VoteStatsDict,
)

DESCRIPTION = """
The HowTheyVote API provides access to data about European Parliament roll-call votes and related data such as biographical information about MEPs and political groups.

## Status
This is an experimental API and the available API endpoints as well as request and response formats may change. We do not guarantee the availability of the API.

## License
The HowTheyVote.eu data is made available under an open license. If you use data published by HowTheyVote.eu please make sure you’ve read the [license terms](https://howtheyvote.eu/about#license) and provide proper attribution.
"""  # noqa: E501

spec = APISpec(
    title="HowTheyVote API",
    version="0.1.0",
    openapi_version="3.1.0",
    servers=[{"url": config.FRONTEND_PUBLIC_URL}],
    plugins=[FlaskPlugin()],
    info={"description": DESCRIPTION},
)

schema_classes = [
    AmendmentAuthorDict,
    MemberDict,
    GroupDict,
    CountryDict,
    CommitteeDict,
    EurovocConceptDict,
    OEILSubjectDict,
    PlenarySessionDict,
    PlenarySessionsQueryResponseDict,
    VoteDict,
    BaseVoteDict,
    BaseVoteWithMemberPositionDict,
    ProcedureDict,
    VoteStatsDict,
    VoteStatsByGroupDict,
    VoteStatsByCountryDict,
    VotePositionCountsDict,
    MemberVoteDict,
    SourceDict,
    LinkDict,
    QueryResponseDict,
    QueryResponseWithFacetsDict,
    FacetOptionDict,
    VotesQueryResponseDict,
    MemberVotesQueryResponseDict,
    RelatedVoteDict,
    Statistics,
]


for schema_cls in schema_classes:
    name = normalize_schema_name(schema_cls)
    schema = get_schema(schema_cls)
    spec.components.schema(name, schema)
