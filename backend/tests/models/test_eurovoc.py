from howtheyvote.models.country import Country
from howtheyvote.models.eurovoc import EurovocConcept


def test_eurovoc_concept_related():
    concept = EurovocConcept["3030"]
    related = concept.related

    expected = {EurovocConcept["3740"], EurovocConcept["3293"], EurovocConcept["c_5a195ffd"]}
    assert related == expected


def test_eurovoc_concept_broader():
    concept = EurovocConcept["c_f7430876"]
    assert concept.broader == {EurovocConcept["3074"]}


def test_eurovoc_concept_geo_area():
    concept = EurovocConcept["245"]
    assert concept.geo_area_code is None
    assert concept.geo_area is None

    concept = EurovocConcept["3774"]
    assert concept.geo_area_code == "GBR"
    assert concept.geo_area == Country["GBR"]
