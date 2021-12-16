"""
separate file for debugging of single tests
"""

import datetime
import logging

from config import developer_ids
from config import repo
from weekly_pr_summary import get_prs_from_date_range

logging.basicConfig(encoding="utf-8", level=logging.WARN)


def test_get_one_closed_not_merged_pr29440():
    """
    Tuesday 16 Aug - one PR was reviewed per dev blog at:
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    expected PR:  https://github.com/python/cpython/pull/29440
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 15, 00, 00, 00)
    end_date = datetime.datetime(2021, 11, 21, 23, 59, 59)

    list_with_pull_report = [repo.get_pull(29440)]

    (
        closed_not_merged_pr_we_care_about,
        pull_requests_reviewed,
    ) = get_prs_from_date_range(
        list_with_pull_report, developer_ids, start_date, end_date
    )

    assert closed_not_merged_pr_we_care_about[0].number == 29440
