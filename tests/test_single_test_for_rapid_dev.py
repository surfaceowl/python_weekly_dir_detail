"""
separate file for debugging of single tests
"""

import datetime
from config import developer_ids
from config import repo
from weekly_pr_summary import get_prs_of_interest


def test_get_one_closed_pr29537():
    """
    Tuesday 16 Nov - one PR was closed per dev blog at:
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    expected PR:  https://github.com/python/cpython/pull/29537
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 16, 00, 00, 00)
    end_date = datetime.datetime(2021, 11, 16, 23, 59, 59)

    list_with_pull_report_29537 = [repo.get_pull(29537)]

    closed_pr_we_care_about, pull_requests_reviewed = get_prs_of_interest(
        list_with_pull_report_29537, developer_ids, start_date, end_date
    )

    assert closed_pr_we_care_about[0].number == 29537
