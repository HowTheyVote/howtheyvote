from howtheyvote.models import Vote


def test_vote_display_title():
    # Only RCV title present
    vote = Vote(title="Title from RCV list", procedure_title=None)
    assert vote.display_title == "Title from RCV list"

    # Only procedure title present
    vote = Vote(title=None, procedure_title="Title from procedure file")
    assert vote.display_title == "Title from procedure file"

    # RCV title and procedure title present
    vote = Vote(title="Title from RCV list", procedure_title="Title from procedure file")
    assert vote.display_title == "Title from RCV list"

    # If the RCV title is very long, prefer the procedure title if it is shorter
    vote = Vote(
        title="Establishment of 'Eurodac' for the comparison of fingerprints for the effective application of Regulation (EU) No 604/2013, for identifying an illegally staying third-country national or stateless person and on requests for the comparison with Eurodac data by Member States' law enforcement authorities and Europol for law enforcement purposes (recast)",
        procedure_title="Eurodac Regulation",
    )
    assert vote.display_title == "Eurodac Regulation"

    # If the RCV title is very long, but the procedure title is even longer, prefer the RCV title
    vote = Vote(
        title="Setting up a special committee on foreign interference in all democratic processes in the European Union, including disinformation",
        procedure_title="Decision on setting up a special committee on foreign interference in all democratic processes in the European Union, including disinformation (INGE 2), and defining its responsibilities, numerical strength and term of office",
    )
    assert (
        vote.display_title
        == "Setting up a special committee on foreign interference in all democratic processes in the European Union, including disinformation"
    )
