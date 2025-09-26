from typing import Any, TypeVar

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.sql import ColumnElement
from sqlalchemy.types import TypeDecorator, TypeEngine

ItemType = TypeVar("ItemType", bound=TypeEngine[Any])


class ListTypeComparator(sa.JSON.Comparator[list[ItemType]]):
    type: "ListType[ItemType]"

    def contains(self, other: ItemType, **kwargs: Any) -> ColumnElement[bool]:
        return self.overlap([other])

    def overlap(self, other: list[ItemType], **kwargs: Any) -> ColumnElement[bool]:
        json_expr = sa.func.json_each(self.expr).table_valued("value")
        return sa.exists(
            sa.select(1)
            .select_from(json_expr)
            .where(
                json_expr.c.value.in_(
                    sa.bindparam("other", unique=True, value=other, type_=self.type.item_type)
                )
            )
        )


class ListType(TypeDecorator[list[ItemType]]):
    """A column type that uses the built-in JSON column type to store list data, but
    automatically (de-)serializes values according to the item type. For example,
    `ListType(sa.Enum(MyEnum))` represents a list of `MyEnum` instances."""

    impl = sa.JSON
    cache_ok = True
    comparator_factory = ListTypeComparator

    def __init__(self, item_type: ItemType):
        super().__init__()

        if isinstance(item_type, type):
            item_type = item_type()

        self.item_type = item_type

    def process_bind_param(
        self, value: list[Any] | None, dialect: Dialect
    ) -> list[ItemType] | None:
        if value is None:
            return None

        item_type = self.item_type
        processor = item_type.dialect_impl(dialect).bind_processor(dialect)

        if isinstance(item_type, TypeDecorator) and isinstance(
            item_type.impl_instance, sa.JSON
        ):

            def processor(value: Any) -> Any:
                return item_type.process_bind_param(value, dialect)

        if not processor:
            return value

        serialized = []

        for item in value:
            serialized_item = processor(item)

            if serialized_item is not None:
                serialized.append(serialized_item)

        return serialized

    def process_result_value(
        self, value: list[ItemType] | None, dialect: Dialect
    ) -> list[Any] | None:
        if value is None:
            return None

        item_type = self.item_type
        processor = item_type.dialect_impl(dialect).result_processor(dialect, None)

        if isinstance(item_type, TypeDecorator) and isinstance(
            item_type.impl_instance, sa.JSON
        ):

            def processor(value: Any) -> Any:
                return item_type.process_result_value(value, dialect)

        if not processor:
            return value

        deserialized = []

        for item in value:
            deserialized_item = processor(item)

            if deserialized_item is not None:
                deserialized.append(deserialized_item)

        return deserialized
