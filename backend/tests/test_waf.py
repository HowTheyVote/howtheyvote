from unittest.mock import call

import pytest

from howtheyvote.scrapers.exceptions import WAFChallengeError
from howtheyvote.waf import run_each_with_waf_token


def test_run_each_with_waf_token(mocker):
    # First call succeeds, second call raises exception, third call succeeds again
    func = mocker.Mock(side_effect=[None, WAFChallengeError(), None])
    solve_waf_challenge = mocker.Mock(return_value="new-token")

    result = run_each_with_waf_token(
        iterable=["first", "second"],
        func=func,
        current_waf_token="current-token",
        solve_waf_challenge=solve_waf_challenge,
        sleep=0,
    )

    assert solve_waf_challenge.call_count == 1
    assert func.call_args_list == [
        call("first", "current-token"),
        call("second", "current-token"),
        call("second", "new-token"),
    ]
    assert result == "new-token"


def test_run_each_with_waf_token_retry_fails(mocker):
    # All calls raise exception
    func = mocker.Mock(side_effect=[WAFChallengeError(), WAFChallengeError()])
    solve_waf_challenge = mocker.Mock(return_value="new-token")

    with pytest.raises(WAFChallengeError):
        run_each_with_waf_token(
            iterable=["item"],
            func=func,
            current_waf_token="current-token",
            solve_waf_challenge=solve_waf_challenge,
            sleep=0,
        )

    assert solve_waf_challenge.call_count == 1
    assert func.call_args_list == [
        call("item", "current-token"),
        call("item", "new-token"),
    ]
