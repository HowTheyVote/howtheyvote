from .helpers import parse_procedure_reference, parse_reference, parse_texts_adopted_reference
from .models import DocumentType


def doceo_document_url(reference: str) -> str | None:
    ref = parse_reference(reference)

    if ref["type"] == DocumentType.C:
        # C documents are documents from other institutions and not available on the EP website
        return None

    base_url = "https://www.europarl.europa.eu/doceo/document"
    file = f"{ref['type'].value}-{ref['term']}-{ref['year']}-{ref['number']:04}_EN.html"
    url = f"{base_url}/{file}"

    return url


def doceo_texts_adopted_url(reference: str) -> str:
    ref = parse_texts_adopted_reference(reference)
    base_url = "https://www.europarl.europa.eu/doceo/document"
    url = f"{base_url}/TA-{ref['term']}-{ref['year']}-{ref['number']:04}_EN.html"

    return url


def oeil_procedure_url(reference: str) -> str:
    ref = parse_procedure_reference(reference)
    base_url = "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference="
    url = f"{base_url}{ref['year']}/{ref['number']:04}({ref['type'].value})"

    return url


def oeil_summary_url(summary_id: int) -> str:
    base_url = "https://oeil.europarl.europa.eu/oeil/en/document-summary"
    return f"{base_url}?id={summary_id}"


def press_release_url(press_release_id: str) -> str:
    base_url = "https://www.europarl.europa.eu/news/en/press-room"
    url = f"{base_url}/{press_release_id}"

    return url
