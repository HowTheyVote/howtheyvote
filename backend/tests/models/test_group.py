import datetime

import pytest

from howtheyvote.models import Group


def test_group_getitem():
    greens = Group["GREEN_EFA"]
    assert isinstance(greens, Group)
    assert greens.code == "GREEN_EFA"

    with pytest.raises(KeyError):
        Group["invalid"]


def test_group_get():
    greens = Group.get("GREEN_EFA")
    assert isinstance(greens, Group)
    assert greens.code == "GREEN_EFA"

    invalid = Group.get("invalid")
    assert invalid is None


def test_group_from_label():
    assert Group.from_label("Group of the Greens/European Free Alliance") == Group["GREEN_EFA"]


def test_group_from_label_short():
    assert Group.from_label("Greens/European Free Alliance") == Group["GREEN_EFA"]


def test_group_from_label_case_insensitive():
    assert Group.from_label("greens/european free alliance") == Group["GREEN_EFA"]


def test_group_from_label_normalized():
    # Note that this doesn't use a proper apostrophe in "People's"
    epp = Group.from_label("Group of the European People's Party")
    assert epp == Group["EPP"]

    # Note that this doesn’t use a proper en dash
    guengl = Group.from_label("The Left group in the European Parliament")
    assert guengl == Group["GUE_NGL"]


def test_group_from_alt_labels():
    guengl = Group.from_label("The Left group in the European Parliament - GUE/NGL")
    assert guengl == Group["GUE_NGL"]


def test_group_from_label_date():
    epp_current = Group.from_label(
        "Group of the European People’s Party (Christian Democrats)",
        date=datetime.date(2025, 1, 1),
    )
    assert epp_current == Group["EPP"]

    epp_2009 = Group.from_label(
        "Group of the European People’s Party (Christian Democrats)",
        date=datetime.date(2019, 1, 1),
    )
    assert epp_2009 == Group["EPP_2009_0"]
