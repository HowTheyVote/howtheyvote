from pathlib import Path

FIXTURES_BASE = Path(__file__).resolve().parent / "data"


def load_fixture(path: str) -> str:
    return FIXTURES_BASE.joinpath(path).read_text()
