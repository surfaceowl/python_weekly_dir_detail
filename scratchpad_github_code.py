import os
from github import Github
import datetime
import logging

# from config import developer_ids
from utilities import check_github_rate_limit

logging.basicConfig(encoding="utf-8", level=logging.WARNING)

github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))
repo = github_host.get_repo("python/cpython")

start_date = datetime.datetime(2021, 11, 15)  # change this (YYYY M DD)

# confirm does "since" get issues updated since a date?
issues_all = repo.get_issues(
    state="all", since=start_date, sort="updated", direction="desc"
)

targeted_issues_15to21nov_titles = [
    "bpo-45831",
    "bpo-42540",
    "bpo-45820",
    "bpo-45826",
    "bpo-45836",
    "bpo-45736",
    "bpo-45835",
    "bpo-45640",
    "bpo-43185",
    "bpo-45507",
    "bpo-45806",
    "bpo-45838",
    "bpo-45837",
    "bpo-42158",
]
check_github_rate_limit()

for idx, issue in enumerate(issues_all):

    if issue.last_modified is not None:
        modified_date = str(datetime.datetime.strftime(issue.last_modified, "%Y-%b-%d"))
    else:
        modified_date = "N/A"

    if issue.created_at is not None:
        created_date = str(datetime.datetime.strftime(issue.created_at, "%Y-%b-%d"))
    else:
        created_date = "N/A"

    if issue.user is not None:
        user = issue.user.login
    else:
        user = None

    if issue.closed_by is not None:
        closed_by = str(issue.closed_by.login)
    else:
        closed_by = "N/A             "

    # if user in developer_ids or closed_by in developer_ids:
    for item in targeted_issues_15to21nov_titles:
        if item in issue.title:
            print(
                f"{str(idx):>5} ",
                f" {issue.number:>5} "
                f"{issue.state:>6}  "
                f"{modified_date:>12} "
                f"{created_date:>12} "
                f"{user:<16} "
                f"{closed_by} "
                f"{str(issue.title)[:10]:<10} "
                f"{issue.events_url}",
            )

check_github_rate_limit()
