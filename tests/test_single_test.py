"""
separate file for debugging of single tests
"""

import datetime
import logging
from cpython_weekly_summary import repo
from cpython_weekly_summary import get_pull_requests_of_interest


def test_get_one_reviewed_pr28089():
    """
    Tuesday 31 Aug - one PR was reviewed per dev blog at:
    https://lukasz.langa.pl/94b5086c-81df-498a-9f8b-f9e06f5d9538/
    expected PR:  https://github.com/python/cpython/pull/28089
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 8, 31, 00, 00, 00)
    end_date = datetime.datetime(2021, 8, 31, 23, 59, 59)

    list_with_pull_report = [repo.get_pull(28089)]

    authored_pr_we_care_about, pull_requests_reviewed = get_pull_requests_of_interest(
        list_with_pull_report, start_date, end_date
    )

    assert authored_pr_we_care_about[0].number == 28089
