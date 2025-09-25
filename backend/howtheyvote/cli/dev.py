import csv
import datetime
from typing import Any, NotRequired, TextIO, TypedDict

import click
import requests
from structlog import get_logger

from ..data import DATA_DIR, DataclassContainer
from ..models import Committee, Country, EurovocConcept, Group, OEILSubject

log = get_logger(__name__)

PUBLICATIONS_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
DATA_ENDPOINT = "https://data.europa.eu/sparql"


class Overrides(TypedDict):
    official_label: NotRequired[str]
    label: NotRequired[str]
    short_label: NotRequired[str]
    alt_labels: NotRequired[list[str]]


GROUP_OVERRIDES: dict[str, Overrides] = {
    "GREEN_EFA": {
        "short_label": "Greens/EFA",
    },
    "GUE_NGL": {
        "label": "The Left in the European Parliament",
        "short_label": "The Left",
        "alt_labels": [
            # Still used by EP MEPs website (as of September 2025)
            "The Left group in the European Parliament - GUE/NGL"
        ],
    },
    "NI": {
        "short_label": "Non-attached",
    },
    "RENEW": {
        "short_label": "Renew",
    },
    "SD": {
        "label": "Progressive Alliance of Socialists and Democrats",
    },
    "EPP": {
        "alt_labels": [
            # Still used by EP MEPs website (as of August 2025)
            "Group of the European People’s Party (Christian Democrats)",
            # Used in VOT lists
            "PPE",
        ],
    },
    "PFE": {
        # Used in VOT lists
        "short_label": "PfE",
    },
}


@click.group()
def dev() -> None:
    """A namespace for commands that are useful during development."""
    pass


@dev.command()
def load_eurovoc() -> None:
    """Load and save a list of terms in the EuroVoc vocabulary."""
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>

    SELECT
      ?term
      ?label
      ?geo_area_code
      (GROUP_CONCAT(DISTINCT ?related_id, ",") as ?related_ids)
      (GROUP_CONCAT(DISTINCT ?broader_id, ",") as ?broader_ids)
      (GROUP_CONCAT(DISTINCT ?alt_label, ",") as ?alt_labels)
    WHERE {
      GRAPH <http://publications.europa.eu/resource/dataset/eurovoc> {
        ?term euvoc:status <http://publications.europa.eu/resource/authority/concept-status/CURRENT>.

        ?term skos:prefLabel ?label_.
        FILTER(lang(?label_) = "en")
        BIND(STR(?label_) as ?label)

        OPTIONAL {
          ?term skos:related ?related.
          ?related euvoc:status <http://publications.europa.eu/resource/authority/concept-status/CURRENT>.
          ?related dc:identifier ?related_id.
        }

        OPTIONAL {
          ?term skos:broader ?broader.
          ?broader euvoc:status <http://publications.europa.eu/resource/authority/concept-status/CURRENT>.
          ?broader dc:identifier ?broader_id.
        }

        OPTIONAL {
          ?term skos:altLabel ?alt_label_.
          FILTER(lang(?alt_label_) = "en")
          BIND(STR(?alt_label_) as ?alt_label)
        }
      }

      OPTIONAL {
        GRAPH <http://publications.europa.eu/resource/dataset/eurovoc_alignment_country> {
          ?term skos:exactMatch ?geo_area.
        }

        GRAPH <http://publications.europa.eu/resource/authority/country> {
          ?geo_area dc:identifier ?geo_area_code.
        }
      }
    }
    GROUP BY ?term ?label ?geo_area_code
    """
    log.info("Retrieving EuroVoc terms")
    results = exec_sparql_query(DATA_ENDPOINT, query)
    container = DataclassContainer(
        dataclass=EurovocConcept,
        file_path=DATA_DIR.joinpath("eurovoc.json"),
        key_attr="id",
    )

    for result in results:
        # `term` is the resource URI (e.g. `http://eurovoc.europa.eu/162`) which contains the
        # ID. We previously used the DC Terms `identifier` property. However, this property is
        # sometimes ambiguous. For example, the domain concept "AGRICULTURE, FORESTRY AND
        # FISHERIES" has the DC Terms identifier `56`, but the correct ID is `100156`.
        if result["term"]["value"]:
            uri = result["term"]["value"]
            _, id_ = uri.rsplit("/", 1)
        else:
            log.warn("Missing resource URI")
            continue

        if result["alt_labels"]["value"]:
            alt_labels = set(result["alt_labels"]["value"].split(","))
        else:
            alt_labels = set()

        if result["related_ids"]["value"]:
            related_ids = set(result["related_ids"]["value"].split(","))
        else:
            related_ids = set()

        if result["broader_ids"]["value"]:
            broader_ids = set(result["broader_ids"]["value"].split(","))
        else:
            broader_ids = set()

        if "geo_area_code" in result:
            geo_area_code = result["geo_area_code"]["value"]
        else:
            geo_area_code = None

        container.add(
            EurovocConcept(
                id=id_,
                label=result["label"]["value"],
                alt_labels=sorted(alt_labels),
                related_ids=sorted(related_ids),
                broader_ids=sorted(broader_ids),
                geo_area_code=geo_area_code,
            )
        )

    container.save()


@dev.command()
def load_countries() -> None:
    """Load and save list of countries and territories from official EU Vocabulary."""
    query = """
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>

    SELECT DISTINCT ?code ?iso_alpha_2 ?label ?alt_label
    FROM <http://publications.europa.eu/resource/authority/country>
    WHERE {
        # Get all countries countries and territories
        # Top level scheme: Countries
        # 0003: Territories
        ?country skos:inScheme ?scheme.
        FILTER(
            ?scheme = <http://publications.europa.eu/resource/authority/country> ||
            ?scheme = <http://publications.europa.eu/resource/authority/country/0003>
        )

        # Only include current countries and territories (exclude deprecated or retired)
        ?country euvoc:status <http://publications.europa.eu/resource/authority/concept-status/CURRENT>.

        # Preferred label
        ?country skos:prefLabel ?label_.
        FILTER(lang(?label_) = "en")
        BIND(STR(?label_) as ?label)

        # Alternative label
        OPTIONAL {
            ?country skosxl:altLabel ?alt_label_node.
            ?alt_label_node skosxl:literalForm ?alt_label_.
            ?alt_label_node euvoc:status ?alt_label_status.
            ?alt_label_node dct:type ?alt_label_type.
            FILTER(
                lang(?alt_label_) = "en" &&
                ?alt_label_status = <http://publications.europa.eu/resource/authority/concept-status/CURRENT> &&
                ?alt_label_type = <http://publications.europa.eu/resource/authority/label-type/LONGLABEL>
            )
            BIND(STR(?alt_label_) as ?alt_label)
        }

        # The ISO-3166-1 2-letter country code. As the EU vocabulary is a superset of the countries
        # listed in the ISO standard, some countries or territories do not have an ISO code.
        OPTIONAL {
            ?country skos:notation ?iso_alpha_2_.
            FILTER(datatype(?iso_alpha_2_) = <http://publications.europa.eu/ontology/euvoc#ISO_3166_1_ALPHA_2>)
            BIND(STR(?iso_alpha_2_) AS ?iso_alpha_2)
        }

        # The Named Authority Code assigned by the EU. In case of countries listed in ISO-3166-1, this
        # this is the 3-letter country code.
        ?country dc:identifier ?code.
    }
    """  # noqa: E501

    log.info("Retrieving countries")
    results = exec_sparql_query(PUBLICATIONS_ENDPOINT, query)
    container = DataclassContainer(
        dataclass=Country,
        file_path=DATA_DIR.joinpath("countries.json"),
        key_attr="code",
    )

    for result in results:
        container.add(
            Country(
                code=result["code"]["value"],
                label=result["label"]["value"],
                iso_alpha_2=result["iso_alpha_2"]["value"]
                if result.get("iso_alpha_2")
                else None,
                alt_label=result["alt_label"]["value"] if result.get("alt_label") else None,
            )
        )

    container.save()


@dev.command()
def load_committees() -> None:
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>

    SELECT ?code ?label ?abbr ?short ?start_date ?end_date
    FROM <http://publications.europa.eu/resource/authority/corporate-body>
    WHERE {
        ?group org:classification <http://publications.europa.eu/resource/authority/corporate-body-classification/EP_CMT>.

        ?group dc:identifier ?code.

        ?group skos:prefLabel ?label.
        FILTER(lang(?label) = "en")

        # The end date is set if the committee isn't active anymore.
        ?group euvoc:startDate ?start_date.
        OPTIONAL { ?group euvoc:endDate ?end_date }

        # Get the current acronym
        OPTIONAL {
            ?group skosxl:altLabel ?abbr_node.
            ?abbr_node skosxl:literalForm ?abbr.
            ?abbr_node dct:type ?abbr_type.
            ?abbr_node euvoc:status ?abbr_status.
            FILTER(
                lang(?abbr) = "en" &&
                ?abbr_type = <http://publications.europa.eu/resource/authority/label-type/ACRONYM> &&
                ?abbr_status = <http://publications.europa.eu/resource/authority/concept-status/CURRENT>
            )
        }
    }
    """  # noqa: E501

    log.info("Retrieving committees")
    results = exec_sparql_query(PUBLICATIONS_ENDPOINT, query)
    committees = DataclassContainer(
        dataclass=Committee,
        file_path=DATA_DIR.joinpath("committees.json"),
        key_attr="code",
    )

    for result in results:
        code = result["code"]["value"]
        code = code.removeprefix("EP_")

        label = result["label"]["value"]
        abbreviation = result["abbr"]["value"] if result.get("abbr") else code

        start_date = datetime.date.fromisoformat(result["start_date"]["value"])
        end_date = (
            datetime.date.fromisoformat(result["end_date"]["value"])
            if result.get("end_date")
            else None
        )

        committees.add(
            Committee(
                code=code,
                label=label,
                abbreviation=abbreviation,
                start_date=start_date,
                end_date=end_date,
            )
        )

    committees.save()


@dev.command()
def load_groups() -> None:
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>

    SELECT ?code ?label ?abbr ?short ?start_date ?end_date
    FROM <http://publications.europa.eu/resource/authority/corporate-body>
    WHERE {
        ?group dct:type <http://publications.europa.eu/resource/authority/corporate-body-classification/EP_GROUP>.

        ?group dc:identifier ?code.

        ?group skos:prefLabel ?label.
        FILTER(lang(?label) = "en")

        # The end date is set if the group isn't active anymore.
        ?group euvoc:startDate ?start_date.
        OPTIONAL { ?group euvoc:endDate ?end_date }

        # Get the current acronym
        OPTIONAL {
            ?group skosxl:altLabel ?abbr_node.
            ?abbr_node skosxl:literalForm ?abbr.
            ?abbr_node dct:type ?abbr_type.
            ?abbr_node euvoc:status ?abbr_status.
            FILTER(
                lang(?abbr) = "en" &&
                ?abbr_type = <http://publications.europa.eu/resource/authority/label-type/ACRONYM> &&
                ?abbr_status = <http://publications.europa.eu/resource/authority/concept-status/CURRENT>
            )
        }

        # Get the current alternative shortname
        OPTIONAL {
            ?group skosxl:altLabel ?short_node.
            ?short_node skosxl:literalForm ?short.
            ?short_node dc:type ?short_type.
            ?short_node euvoc:status ?short_status.
            FILTER(
                lang(?short) = "en" &&
                ?short_type = <http://publications.europa.eu/resource/authority/label-type/SHORTLABEL> &&
                ?short_status = <http://publications.europa.eu/resource/authority/concept-status/CURRENT>
            )
        }
    }
    """  # noqa: E501

    log.info("Retrieving groups")
    results = exec_sparql_query(PUBLICATIONS_ENDPOINT, query)
    groups = DataclassContainer(
        dataclass=Group,
        file_path=DATA_DIR.joinpath("groups.json"),
        key_attr="code",
    )

    for result in results:
        code = result["code"]["value"]
        code = code.removeprefix("EP_GROUP_")

        official_label = result["label"]["value"]
        label = result["short"]["value"] if result.get("short") else None

        if not label:
            label = official_label.removeprefix("Group of the ").removesuffix(" Group")

        short_label = result["abbr"]["value"] if result.get("abbr") else label

        alt_labels = _load_alt_labels(code)
        overrides = GROUP_OVERRIDES.get(code)

        if overrides:
            if overrides.get("official_label"):
                alt_labels.add(official_label)
                official_label = overrides["official_label"]
            if overrides.get("label"):
                alt_labels.add(label)
                label = overrides["label"]
            if overrides.get("short_label"):
                alt_labels.add(short_label)
                short_label = overrides["short_label"]
            alt_labels.update(overrides.get("alt_labels", []))

        alt_labels.discard(official_label)
        alt_labels.discard(label)
        alt_labels.discard(short_label)

        start_date = datetime.date.fromisoformat(result["start_date"]["value"])
        end_date = (
            datetime.date.fromisoformat(result["end_date"]["value"])
            if result.get("end_date")
            else None
        )

        groups.add(
            Group(
                code=code,
                official_label=official_label,
                label=label,
                short_label=short_label,
                start_date=start_date,
                end_date=end_date,
                alt_labels=sorted(alt_labels),
            )
        )

    groups.save()


def _load_alt_labels(group_code: str) -> set[str]:
    # Loads a list of all current and previous alternative labels for the given political
    # group. Probably there's some elegant way to make the main SPARQL query above return
    # nested data that already includes these, but that's above my capabilities.
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>

    SELECT ?label ?type ?start_date ?end_date
    WHERE {
        ?group dc:identifier ?code.
        FILTER(?code = "EP_GROUP_{{group_code}}")

        ?group skosxl:altLabel ?label_node.
        ?label_node skosxl:literalForm ?label.
        FILTER(lang(?label) = "en")
    }
    """

    query = query.replace("{{group_code}}", group_code)
    results = exec_sparql_query(PUBLICATIONS_ENDPOINT, query)
    return set(r["label"]["value"] for r in results)


@dev.command()
@click.argument("file", type=click.File("r"))
def load_oeil_subjects(file: TextIO) -> None:
    """Loads a list of procedure subjects as used by the Legislative Observatory. A
    list of all subjects is provided as a PDF file on the OEIL website[^1]. Alternatively,
    an Excel version can be requested by contacting the OEIL webmaster. Convert the list
    to a CSV file with the columns "Code", "Parent", "Description", then run this command
    to load it into HowTheyVote.

    [^1]: https://oeil.secure.europarl.europa.eu/oeil/en/find-out-more#widget5
    """
    subjects = DataclassContainer(
        dataclass=OEILSubject,
        file_path=DATA_DIR.joinpath("oeil_subjects.json"),
        key_attr="code",
    )

    dialect = csv.Sniffer().sniff(file.read(), delimiters=",;")
    file.seek(0)
    reader = csv.DictReader(file, dialect=dialect)

    for row in reader:
        subjects.add(
            OEILSubject(
                code=row["Code"],
                label=row["Description"],
                parent_code=row["Parent"],
            )
        )

    subjects.save()


def exec_sparql_query(endpoint: str, query: str) -> Any:
    response = requests.post(
        endpoint,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
    )
    return response.json()["results"]["bindings"]
