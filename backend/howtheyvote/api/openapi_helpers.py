import ast
import datetime
from enum import Enum
from types import NoneType, UnionType
from typing import Annotated, Any, TypedDict, get_args, get_origin, is_typeddict

from ..helpers import get_attribute_docstrings, get_class_ast, get_normalized_docstring


def get_schema(schema_cls: type) -> dict[str, Any]:
    """Generate a OpenAPI/JSON Schema for the given class."""

    if not is_typeddict(schema_cls):
        raise Exception("Only TypedDict is supported.")

    cls_docstring = get_normalized_docstring(schema_cls)
    annotations = schema_cls.__annotations__
    non_inherited_annotations = _get_annotated_attributes(schema_cls)
    attr_docstrings = get_attribute_docstrings(schema_cls)

    props: dict[str, dict[Any, Any]] = {}
    required: list[str] = []

    for name, prop_type in annotations.items():
        if name not in non_inherited_annotations:
            continue

        definition = get_property_definition(prop_type)

        if "required" in definition:
            if definition["required"]:
                required.append(name)
            del definition["required"]

        if attr_docstrings.get(name):
            definition["description"] = attr_docstrings.get(name)

        props[name] = definition

    all_of = []

    for base_cls in schema_cls.__orig_bases__:  # type: ignore[attr-defined]
        if base_cls == TypedDict:
            continue

        all_of.append({"$ref": _ref(base_cls)})

    schema: dict[str, Any] = {
        "type": "object",
        "properties": props,
    }

    if cls_docstring:
        schema["description"] = cls_docstring

    if all_of:
        schema["allOf"] = all_of

    if required:
        schema["required"] = required

    return schema


def get_property_definition(prop_type: Any) -> dict[str, Any]:
    """Returns a JSON Schema property definition for the given type or class. This only handles
    types and classes that we currently use in `howtheyvote.api.serializers`."""

    if prop_type is str:
        return {
            "type": "string",
            "required": True,
        }

    if prop_type is int:
        return {
            "type": "integer",
            "required": True,
        }

    if prop_type is float:
        return {
            "type": "number",
            "required": True,
        }

    if prop_type is bool:
        return {
            "type": "boolean",
            "required": True,
        }

    if prop_type is datetime.date:
        return {
            "type": "string",
            "format": "date",
            "required": True,
        }

    if prop_type is datetime.datetime:
        return {
            "type": "string",
            "format": "date-time",
            "required": True,
        }

    if isinstance(prop_type, type) and issubclass(prop_type, Enum):
        return {
            "type": "string",
            "enum": [member.value for member in prop_type],
            "required": True,
        }

    if get_origin(prop_type) is list:
        type_args = get_args(prop_type)
        item_type = type_args[0]
        item_definition = get_property_definition(item_type)

        if "required" in item_definition:
            del item_definition["required"]

        return {
            "type": "array",
            "required": True,
            "items": item_definition,
        }

    if get_origin(prop_type) is dict:
        type_args = get_args(prop_type)
        key_type, value_type = type_args

        if key_type is not str:
            raise Exception("Only dicts with string keys are supported.")

        value_definition = get_property_definition(value_type)

        if "required" in value_definition:
            del value_definition["required"]

        return {
            "type": "object",
            "required": True,
            "additionalProperties": value_definition,
        }

    if isinstance(prop_type, UnionType):
        type_args = get_args(prop_type)

        # This currently doesn't handle union types of more than two non-None types
        # because we haven't had a need for it so far.
        if len(type_args) == 2 and NoneType in type_args:
            other_type = next(arg for arg in type_args if arg is not NoneType)
            definition = get_property_definition(other_type)
            definition["required"] = False
            return definition

    if get_origin(prop_type) is Annotated:
        # We use the annotation metadata as example values
        wrapped_type, example = get_args(prop_type)
        definition = get_property_definition(wrapped_type)
        definition["example"] = example
        return definition

    if isinstance(prop_type, type) and is_typeddict(prop_type):
        return {
            "$ref": _ref(prop_type),
            "required": True,
        }

    raise Exception(f"Could not get property definition for {prop_type}")


def _get_annotated_attributes(type_: type) -> set[str]:
    """Python doesn't allow checking if an attribute of a `TypedDict` was inherited from
    another `TypedDict` or not, so this class analyzes the AST to return a list of all
    attributes that have been defined explicitly and not inherited."""
    class_def = get_class_ast(type_)
    attrs = set()

    for stmt in class_def.body:
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                attrs.add(str(stmt.target.id))

    return attrs


def _ref(type_: type) -> str:
    normalized_name = normalize_schema_name(type_)
    return f"#/components/schemas/{normalized_name}"


def normalize_schema_name(type_: type) -> str:
    return type_.__name__.removesuffix("Dict")
