from howtheyvote.links import doceo_document_url, oeil_procedure_url, press_release_url


def test_doceo_document_url():
    url = doceo_document_url("A10-0110/2025")
    assert url == "https://www.europarl.europa.eu/doceo/document/A-10-2025-0110_EN.html"


def test_oeil_procedure_url():
    url = oeil_procedure_url("2025/2024(INI)")
    assert (
        url
        == "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2025/2024(INI)"
    )


def test_press_release_url():
    url = press_release_url("20250704IPR29451")
    assert url == "https://www.europarl.europa.eu/news/en/press-room/20250704IPR29451"
