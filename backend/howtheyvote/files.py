from pathlib import Path

import requests
from PIL import Image
from structlog import get_logger

from . import config

log = get_logger(__name__)


def file_path(path: str | Path) -> Path:
    absolute_path = config.FILES_DIR / Path(path)
    relative_path = absolute_path.relative_to(config.FILES_DIR)
    return config.FILES_DIR / relative_path


def member_photo_path(member_id: int, size: int | None = None) -> Path:
    if size:
        return file_path(f"members/{member_id}-{size}.jpg")

    return file_path(f"members/{member_id}.jpg")


def member_sharepic_path(member_id: int) -> Path:
    return file_path(f"members/sharepic-{member_id}.png")


def vote_sharepic_path(vote_id: int) -> Path:
    return file_path(f"votes/sharepic-{vote_id}.png")


def download_file(url: str, path: str | Path) -> Path | None:
    # Ensure that the download path is inside the files directory
    path = file_path(path)
    ensure_parent(path)

    with requests.get(url, stream=True, timeout=config.REQUEST_TIMEOUT) as res:
        res.raise_for_status()

        with open(path, "wb") as f:
            for chunk in res.iter_content():
                f.write(chunk)

    return path


def ensure_parent(path: str | Path) -> None:
    path = file_path(path)
    parent_dir = Path(path).parent

    if not parent_dir.exists():
        parent_dir.mkdir(parents=True)


def image_thumb(
    input_path: str | Path,
    output_path: str | Path,
    format: str | None = None,
    size: int | None = None,
) -> Path:
    output_path = file_path(output_path)

    with Image.open(input_path) as image:
        thumb = image.copy()

        if size:
            thumb.thumbnail((104, 104))

        if not format:
            format = image.format

        thumb.save(output_path, format=format, optimize=True)

    return output_path
