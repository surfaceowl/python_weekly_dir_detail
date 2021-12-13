"""
separate file for debugging of single tests
"""

import datetime

from config import developer_ids
from config import repo
from weekly_pr_summary import get_prs_of_interest


def test_all_prs_on_16nov_search_by_list_of_pr():
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
    reviewed_pr_expected = [29601]

    # assemble subset of targeted pr objects for faster testing
    pull_requests_targeted = [
        pull_request
        for pull_request in [
            repo.get_pull(target_pr_number) for target_pr_number in pr_we_expect_to_find
        ]
    ]

    # pull results using our functions
    pr_we_care_about, pull_requests_reviewed = get_prs_of_interest(
        pull_requests_targeted, developer_ids, start_date, end_date
    )

    pr_numbers_found = [pr.number for pr in pr_we_care_about]
    all_expected_prs_found = bool(set(pr_numbers_found) == set(pr_we_expect_to_find))
    all_expected_reviewed_prs_found = bool(
        pull_requests_reviewed == reviewed_pr_expected
    )

    assert all_expected_prs_found and all_expected_reviewed_prs_found
