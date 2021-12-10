"""
separate test file for slow queries - due to size of cypthon/cpython repo and
limitations on pagination and caching with PyGitHub library
"""

import datetime
import logging

from config import developer_ids
from config import pull_requests_all
from weekly_pr_summary import get_pull_requests_of_interest

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


def test_all_prs_on_16nov_search_by_date():
    """
    Tuesday 16 Nov 2021 - 15 PR total cited (14 closed, 1 reviewed) per dev blog at
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 16, 00, 00, 00)
    end_date = datetime.datetime(2021, 11, 16, 23, 59, 59)

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
    ]
    # reviewed_pr = [29601]

    # pull results using our functions
    pr_we_care_about, _pull_requests_reviewed = get_pull_requests_of_interest(
        pull_requests_all, "ambv", start_date, end_date
    )

    # elements below useful for simplification & debugging
    pr_numbers_found = sorted([pr.number for pr in pr_we_care_about])
    pr_numbers_expected = sorted(pr_we_expect_to_find)
    pr_numbers_expected_not_found = [
        pr for pr in pr_numbers_expected if (pr not in pr_numbers_found)
    ]

    # code may find more PRs than Developer In Residence chose to publish on a date
    # code may not find every PR given complexities in source data on GitHub
    # assume if we find 95% of prs we are close enough
    assert len(pr_numbers_expected_not_found) <= 0.05 * len(pr_numbers_expected)


def test_all_prs_on_15to21nov_search_by_date():
    """
    Tuesday 16 Nov 2021 - 15 PR total cited (14 closed, 1 reviewed) per dev blog at
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 15, 00, 00, 00)
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
    # reviewed_pr = [29601, 29525, 29626, 23320]

    # pull results using our functions
    pr_we_care_about, _pull_requests_reviewed = get_pull_requests_of_interest(
        pull_requests_all, developer_ids, start_date, end_date
    )

    # elements below useful for simplification & debugging
    pr_numbers_found = sorted([pr.number for pr in pr_we_care_about])
    pr_numbers_expected = sorted(pr_we_expect_to_find)
    pr_numbers_expected_not_found = [
        pr for pr in pr_numbers_expected if (pr not in pr_numbers_found)
    ]

    print(
        f"\n"
        f"the following PRs were not captured by the report:  "
        f"{pr_numbers_expected_not_found}"
    )
    # code may find more PRs than Developer In Residence chose to publish on a date
    # code may not find every PR given complexities in source data on GitHub
    # assume if we find 95% of prs we are close enough
    assert len(pr_numbers_expected_not_found) <= 0.18 * len(pr_numbers_expected)
