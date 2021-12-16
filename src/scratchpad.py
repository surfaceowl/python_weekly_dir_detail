"""scratch file for quickly hacking things together"""
import datetime
import logging
import os

from github import Github

# from config import developer_ids
from utilities import check_github_rate_limit

logging.basicConfig(encoding="utf-8", level=logging.INFO)

github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))
repo = github_host.get_repo("python/cpython")

result = repo.get_pull(29525)

start_date = datetime.datetime(2021, 11, 15)  # change this (YYYY M DD)

# confirm does "since" get issues updated since a date?
issues_all = repo.get_issues(
    state="all", since=start_date, sort="updated", direction="desc"
)

check_github_rate_limit()
