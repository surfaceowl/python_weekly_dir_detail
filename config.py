""""
key configuration values
"""
import datetime
import os

from github import Github

# change these values - user-set input search parameters
# GITHUB_ACCESS_TOKEN must be set in env var
target_repo = "python/cpython"
developer_ids = ["ambv"]  # list in case you want more than one;
buildbot_ids = ["miss-islington"]  # approved bots that can merge prs we need to count
start_date = datetime.datetime(2021, 11, 15)  # change this (YYYY M DD)
end_date = datetime.datetime(2021, 11, 21)  # change this
end_date_buffer = 2  # change this; assume 2 days
# num days added to end_date to capture updates by bots after DIR specified period


# computed parameters
github_token = os.environ.get("GITHUB_ACCESS_TOKEN")
github_host = Github(login_or_token=github_token, per_page=100)
repo = github_host.get_repo(target_repo)
# modify end_date to capture all 24 hours of the last day
end_date = end_date + datetime.timedelta(days=1)

# no date filter on get_pulls() method yet; state inputs must be single string
# get all PRs, so we can capture closed, merged and reviewed together
# sort via updated in reverse order; so we can stop iterating over API and
# stay below our API rate limit
pull_requests_all = repo.get_pulls(state="all", sort="updated", direction="descending")

# pull all issues, filter down to report date start
issues_all = repo.get_issues(
    state="all", since=start_date, sort="updated", direction="desc"
)
