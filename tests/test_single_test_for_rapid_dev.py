"""
separate file for debugging of single tests
"""

import datetime

from config import developer_ids
from config import pull_requests_all
from config import repo
from weekly_pr_summary import get_prs_of_interest


def test_all_prs_on_15to21nov_search_by_date():
    """
    Tuesday 16 Nov 2021 - 15 PR total cited (14 closed, 1 reviewed) per dev blog at
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    includes date of 11/12 to capture PR 29525  closed just before report period
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 12, 00, 00, 00)  # note early day
    end_date = datetime.datetime(2021, 11, 21, 23, 59, 59)

    pr_we_expect_to_find = [
        29596,
        29598,
        29597,
        29600,
        29590,
        29586,
        29585,
        29571,
        29583,
        29584,
        29603,
        29604,
        29589,
        29602,
        29601,
        29618,
        29389,
        29612,
        29605,
        29509,
        29440,
        29152,
        29195,
        29621,
        29620,
        29619,
        29623,
        29622,
        29525,
        29640,
        29628,
        29029,
        29636,
        29634,
        29630,
        29629,
        29643,
        29626,
        23230,
        29646,
        29661,
        23230,
        29656,
        29657,
        29539,
    ]
    reviewed_pr = [29601, 29525, 29626, 23230]

    # pull results using our functions
    pr_we_care_about, _pull_requests_reviewed = get_prs_of_interest(
        pull_requests_all, developer_ids, start_date, end_date
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
    assert found_all_prs and found_all_reviewed_prs
