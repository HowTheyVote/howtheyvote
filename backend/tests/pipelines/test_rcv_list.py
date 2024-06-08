import datetime

import pytest

from howtheyvote.pipelines import DataUnavailableError, RCVListPipeline


def test_run_source_not_available(responses, db_session):
    with pytest.raises(DataUnavailableError):
        pipe = RCVListPipeline(term=9, date=datetime.date(2024, 4, 10))
        pipe.run()
