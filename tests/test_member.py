from ep_votes.member import parse_name


def test_parse_name():
    assert parse_name("Katarina BARLEY") == ("Katarina", "BARLEY")


def test_parse_name_multiple_first_names():
    assert parse_name("Marek Paweł BALT") == ("Marek Pawel", "BALT")
    assert parse_name("Anna-Michelle ASIMAKOPOULOU") == (
        "Anna-Michelle",
        "ASIMAKOPOULOU",
    )


def test_parse_name_multiple_last_names():
    assert parse_name("Pablo ARIAS ECHEVERRÍA") == ("Pablo", "ARIAS ECHEVERRIA")
    assert parse_name("Attila ARA-KOVÁCS") == ("Attila", "ARA-KOVACS")


def test_parse_name_middle_initial():
    assert parse_name("Jakop G. DALUNDE") == ("Jakop G.", "DALUNDE")


def test_parse_name_special_affixes():
    assert parse_name("David McALLISTER") == ("David", "McALLISTER")
    assert parse_name("Pilar del CASTILLO VERA") == ("Pilar", "del CASTILLO VERA")
    assert parse_name("Rosa d'AMATO") == ("Rosa", "d'AMATO")
    assert parse_name("Peter van DALEN") == ("Peter", "van DALEN")
    assert parse_name("Sophia in 't VELD") == ("Sophia", "in 't VELD")
    assert parse_name("Ursula von der LEYEN") == ("Ursula", "von der LEYEN")
    assert parse_name("Sophie in ’t VELD") == ("Sophie", "in 't VELD")


def test_parse_name_special_chars():
    assert parse_name("Jörg MEUTHEN") == ("Jorg", "MEUTHEN")
    assert parse_name("Leïla CHAIBI") == ("Leila", "CHAIBI")
    assert parse_name("Stéphane SÉJOURNÉ") == ("Stephane", "SEJOURNE")
