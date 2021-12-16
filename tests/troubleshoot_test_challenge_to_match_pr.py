"""
separate test to troubleshoot PRS that have been difficult to capture in other tests
named differently so it does not run automatically when running pytest, as it
duplicates the `pr_slow` tests
"""

import datetime
import logging

from config import developer_ids
from config import pull_requests_all
from utilities import check_github_rate_limit
from weekly_pr_summary import get_pr_objects_from_pr_numbers

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


def test_all_prs_on_15to21nov_search_by_date_find_challenge_to_match_pr():
    """
    Tuesday 16 Nov 2021 - 15 PR total cited (14 closed, 1 reviewed) per dev blog at
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    includes date of 11/12 to capture PR 29525  closed just before report period
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 12, 00, 00, 00)  # note early day
    end_date = datetime.datetime(2021, 11, 21, 23, 59, 59)

    pr_we_expect_to_find = [29525, 29583, 29626]
    reviewed_pr = [29525, 29583, 29626]

    # pull results using our functions
    (
        _user_input_list,
        pr_we_care_about,
        _pull_requests_reviewed,
    ) = get_pr_objects_from_pr_numbers(
        pull_requests_all, developer_ids, start_date, end_date, pr_we_expect_to_find
    )

    # elements below useful for simplification & debugging
    prs_found = sorted([pr.number for pr in pr_we_care_about])
    prs_expected = sorted(pr_we_expect_to_find)
    prs_expected_not_found = [pr for pr in prs_expected if (pr not in prs_found)]

    pr_reviews_not_found = [pr for pr in reviewed_pr if (pr not in prs_found)]

    # code may find more PRs than Developer In Residence chose to publish on a date
    # assume if we find 97% of prs we are close enough

    found_all_prs = bool(not prs_expected_not_found)  # True if empty list
    found_all_reviewed_prs = bool(not pr_reviews_not_found)  # True if empty list
    check_github_rate_limit()
    assert found_all_prs and found_all_reviewed_prs
