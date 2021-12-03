# script to pull select data from GitHub for cpython Developer In Residence weekly reporting
# collect final results in a list, to make html ready lines to drop into the weekly blog
# requires env var:  GITHUB_ACCESS_TOKEN, a valid access token from your GitHub account

import datetime
import os

from github import Github

# setup search parameters
github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))  # must be set in env var
repo = github_host.get_repo("python/cpython")  # target repo
developer_ids = ["ambv"]  # list in case you want more than one
report_start_date = datetime.datetime(2021, 11, 15)  # change this
report_end_date = datetime.datetime(2021, 11, 21)  # change this

# no date filter on get_pulls() method yet; state inputs must be single string
pull_requests_closed = repo.get_pulls(
    state="closed", sort="created", direction="ascending"
)

# pull_requests_reviewed = repo.get_pulls(state="reviewed", sort="created", direction="ascending")
# pull_requests_all = [pull_requests_closed, pull_requests_reviewed]


def get_merged_pull_request_summaries(pull_request_input_set):
    summaries = []
    for each_pull_request in pull_request_input_set:
        # filter out drivers of AttributeErrors
        if (
            each_pull_request.merged_by is not None
            and each_pull_request.merged_at is not None
        ):
            # keep only PRs we are interested in
            if (
                each_pull_request.state == "closed"
                and each_pull_request.merged_by.login in developer_ids
                and report_start_date <= each_pull_request.merged_at <= report_end_date
            ):
                link_text = "closed GH-" + str(each_pull_request.number)
                # use html_url attribute for human friendly link, vs api link at url attribute
                link_url = "<a href=" + str(f"{each_pull_request.html_url} >{link_text}</a>")
            try:
                friendly_title = each_pull_request.title.split(": ", 1)[1]
            except IndexError:
                friendly_title = (
                    str(f"[{each_pull_request.base.ref}]: ") + each_pull_request.title
                )

            summaries.append(
                f"{each_pull_request.merged_at.strftime('%A')} \
                 {each_pull_request.base.ref:>5}  \
                 {link_url}  \
                 {friendly_title}"
            )
        else:
            continue

    return summaries


# merge results for different sets of pull requests
# for pull_request_group in pull_requests_all:
final_summary = get_merged_pull_request_summaries(pull_requests_closed)

# clean up for easy copy & paste
final_summary.sort(key=lambda x: x[:5], reverse=True)
for item in final_summary:
    print(item[5:])  # cut the branch name from prefix to mirror current blog format
