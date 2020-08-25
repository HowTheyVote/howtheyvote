from ep_votes.group import Group

def test_from_str():
    assert Group.from_str('Group of the Greens/European Free Alliance') == Group.GREENS
