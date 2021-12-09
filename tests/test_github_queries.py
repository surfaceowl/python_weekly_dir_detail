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

    closed_pr_we_care_about, pull_requests_reviewed = get_pull_requests_of_interest(
        list_with_pull_report_29537, start_date, end_date
    )

    assert closed_pr_we_care_about[0].number == 29537


def test_get_one_authored_pr28044():
    """
    Monday 30 Aug - one PR was authored per dev blog at:
    https://lukasz.langa.pl/94b5086c-81df-498a-9f8b-f9e06f5d9538/
    expected PR:  https://github.com/python/cpython/pull/28044
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 8, 30, 00, 00, 00)
    end_date = datetime.datetime(2021, 8, 30, 23, 59, 59)

    list_with_pull_report = [repo.get_pull(28044)]

    authored_pr_we_care_about, pull_requests_reviewed = get_pull_requests_of_interest(
        list_with_pull_report, start_date, end_date
    )

    assert authored_pr_we_care_about[0].number == 28044


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
