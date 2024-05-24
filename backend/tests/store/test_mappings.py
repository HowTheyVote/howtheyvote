from howtheyvote.models import Country, EurovocConcept
from howtheyvote.store import CompositeRecord
from howtheyvote.store.mappings import map_vote


def test_map_vote_eurovoc_concepts_deduplication():
    record = CompositeRecord(
        group_key="12345",
        data={
            "timestamp": ["2024-01-01T00:00:00Z"],
            "eurovoc_concepts": [["4514", "5585", "4514"]],
            "member_votes": [[]],
        },
    )

    vote = map_vote(record)
    expected = {EurovocConcept["4514"], EurovocConcept["5585"]}

    assert len(vote.eurovoc_concepts) == 2
    assert set(vote.eurovoc_concepts) == expected


def test_map_vote_eurovoc_concepts_geo_areas():
    record = CompositeRecord(
        group_key="12345",
        data={
            "timestamp": ["2024-01-01T00:00:00Z"],
            "geo_areas": [["XXI"], ["GBR"]],
            "member_votes": [[]],
        },
    )

    vote = map_vote(record)
    expected = {Country["XXI"], Country["GBR"]}

    assert len(vote.geo_areas) == 2
    assert set(vote.geo_areas) == expected


def test_map_vote_geo_areas_dedpuplication():
    record = CompositeRecord(
        group_key="12345",
        data={
            "timestamp": ["2024-01-01T00:00:00Z"],
            "geo_areas": [["BEL", "BEL"]],
            "member_votes": [[]],
        },
    )

    vote = map_vote(record)

    assert len(vote.geo_areas) == 1
    assert vote.geo_areas == {Country["BEL"]}
