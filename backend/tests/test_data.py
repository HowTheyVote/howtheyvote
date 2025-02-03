import dataclasses
import json
from pathlib import Path
from typing import Any

from howtheyvote.data import DataclassContainer, DeserializableDataclass


@dataclasses.dataclass
class ExampleDataclass(DeserializableDataclass):
    id: str
    label: str

    @classmethod
    def from_dict(cls, data: dict[Any, Any]) -> "ExampleDataclass":
        return cls(**data)


def test_dataclass_container_save(tmp_path: Path):
    file_path = tmp_path.joinpath("container.json")

    container = DataclassContainer(
        dataclass=ExampleDataclass,
        file_path=file_path,
        key_attr="id",
    )

    container.add(ExampleDataclass(id="foo", label="bar"))
    container.save()

    expected = json.dumps([{"id": "foo", "label": "bar"}], indent=2)
    assert file_path.read_text() == expected


def test_dataclass_container_save_sorted(tmp_path: Path):
    file_path = tmp_path.joinpath("container.json")

    container = DataclassContainer(
        dataclass=ExampleDataclass,
        file_path=file_path,
        key_attr="id",
    )

    container.add(ExampleDataclass(id="foo", label="foo"))
    container.add(ExampleDataclass(id="bar", label="bar"))
    container.save()

    expected = json.dumps(
        [
            {"id": "bar", "label": "bar"},
            {"id": "foo", "label": "foo"},
        ],
        indent=2,
    )
    assert file_path.read_text() == expected


def test_dataclass_container_load(tmp_path: Path):
    file_path = tmp_path.joinpath("container.json")

    data = [{"id": "foo", "label": "bar"}]
    file_path.write_text(json.dumps(data))

    container = DataclassContainer(
        dataclass=ExampleDataclass,
        file_path=file_path,
        key_attr="id",
    )

    container.load()

    assert container.get("foo") == ExampleDataclass(id="foo", label="bar")


def test_dataclass_container_iter():
    container = DataclassContainer(
        dataclass=ExampleDataclass,
        file_path="",
        key_attr="id",
    )

    assert list(container) == []
    container.add(ExampleDataclass(id="foo", label="bar"))
    assert list(container) == [ExampleDataclass(id="foo", label="bar")]
