"""
separate test file for slow queries - due to size of cypthon/cpython repo and
limitations on pagination and caching with PyGitHub library
"""

import datetime

from weekly_pr_summary import get_pull_requests_of_interest
from weekly_pr_summary import pull_requests_all


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
    reviewed_pr = [29601]

    # pull results using our functions
    pr_we_care_about, _pull_requests_reviewed = get_pull_requests_of_interest(
        pull_requests_all, "ambv", start_date, end_date
    )

    # elements below useful for simplification & debugging
    pr_numbers_found = [pr.number for pr in pr_we_care_about]
    results_found = sorted(set(pr_numbers_found))
    pr_numbers_expected = sorted(set(pr_we_expect_to_find))
    pr_numbers_expected_not_found = [
        pr for pr in pr_numbers_expected if (pr not in pr_numbers_found)
    ]

    # code may find more PRs than Developer In Residence chose to publish on a date
    # code may not find every PR given complexities in source data on GitHub
    # assume if we find 95% of prs we are close enough
    assert len(pr_numbers_expected_not_found) <= 0.05 * len(pr_numbers_expected)
