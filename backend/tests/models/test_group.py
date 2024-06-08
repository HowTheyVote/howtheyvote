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
    epp = Group.from_label("Group of the European People's Party (Christian Democrats)")
    assert epp == Group["EPP"]

    guengl = Group.from_label("Group of the European United Left - Nordic Green Left")
    assert guengl == Group["GUE_NGL"]
