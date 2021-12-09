"""
test github queries for specific results we know were reported on various
weekly Developer In Residence Reports
15 Nov - 21 Nov 2021: https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
30 Aug - 5 Sept 2021:  https://lukasz.langa.pl/94b5086c-81df-498a-9f8b-f9e06f5d9538/

Tests can take some time since PyGitHub does not enable limit all queries by date and
cpython/cpython is a large repo (e.g. query for PR pulls from entire repo (unlike
Issues API, where you can spec a "since" date).  Ideally we'd only like PRs modified
between date ranges to pull less, but that is client-side responsibility
"""

import datetime
import logging
import os
import requests

import github.GithubException
from github import Github

from cpython_weekly_summary import github_host
from cpython_weekly_summary import repo
from cpython_weekly_summary import developer_ids
from cpython_weekly_summary import pull_requests_all
from cpython_weekly_summary import get_pull_requests_of_interest


def test_get_pull_requests_of_interest_PR29537():
    """
    Tuesday 16 Nov - one PR was closed per dev blog at:
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    expected PR:  https://github.com/python/cpython/pull/29537
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 16)
    end_date = datetime.datetime(2021, 11, 16)

    list_with_pull_report_29537 = [repo.get_pull(29537)]

    pull_reports_we_care_about, pull_requests_reviewed = get_pull_requests_of_interest(
        list_with_pull_report_29537, start_date, end_date
    )

    expected_pr = pull_reports_we_care_about[0]
    assert expected_pr.number == 29537
