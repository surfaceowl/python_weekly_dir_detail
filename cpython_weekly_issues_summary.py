# script to pull select data from GitHub for cpython Developer In Residence
# weekly reporting.
# collect final results in a list, to make html ready lines to drop into the weekly blog
# requires env var:  GITHUB_ACCESS_TOKEN, a valid access token from your GitHub account
# GitHub API issues reference:  https://docs.github.com/en/rest/reference/issues
# PyGitHub issues API: https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html?highlight=get_issues#github.Repository.Repository.get_issues

import datetime
import os

from github import Github

# setup search parameters
github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))  # must be set in env var
repo = github_host.get_repo("python/cpython")  # target repo
developer_ids = ["ambv"]  # list in case you want more than one
report_start_date = datetime.datetime(2021, 11, 15)  # change this
report_end_date = datetime.datetime(2021, 11, 21)  # change this

github_ratelimit = github_host.get_rate_limit()
print(f"github ratelimit status is: {github_ratelimit}")

# pull all issues, filter down to report date start
all_issues = repo.get_issues(state="all",
                             since=report_start_date,
                             sort="updated",
                             direction="asc")
counter = 0
opened_by_ambv = 0
closed_by_ambv = 0

print("\n")
print(f"github ratelimit status is: {github_ratelimit}")


def filter_issues(input_issues):
    issues_opened = []
    issues_closed = []
    combined_issues = []
    
    for issue in all_issues:
        if issue.state == "closed":
            if issue.closed_by.login in developer_ids:
                issues_closed.append(issue)
        else:
            if issue.user.login is not None:
                if issue.user.login in developer_ids:
                    issues_opened.append(issue)

    combined_issues = sorted(issues_opened + issues_closed, key=lambda x:x.updated_at)
        
    return combined_issues


def format_issues(input_issues):
    """
    extract and formats key fields into an output list.
    :param input_issues: list of tuples containing issues of interest
    :return: list of tuples containing reformatted key output fields
    """
    report_issues = []

    for issue in input_issues:

        # determine branch based on common PR naming pattern with [X.Y] branch prefix
        if "[3." not in issue.title:
            branch_name = "[main]"
        else:
            branch_name = str(issue.title).split(" ", 2)[0]

        match issue.state:
            case "open":
                # issues we authored
                if issue.user.login in developer_ids \
                        and issue.updated_at >= report_start_date:
                    report_issues.append(
                        tuple(
                            (
                                f"{issue.updated_at}",
                                "Issue",
                                "opened",
                                f"{branch_name.rjust(6)}",
                                f"{issue.url}",
                                f"{issue.title}",
                            )
                        )
                    )

                # issues we reviewed
                if issue.user.login in developer_ids \
                    and issue.updated_at >= report_start_date:
                    report_issues.append(
                        tuple(
                            (
                                f"{issue.updated_at}",
                                "Issue",
                                "reviewed",
                                f"{branch_name.rjust(6)}",
                                f"{issue.url}",
                                f"{issue.title}",
                            )
                        )
                    )

            # issues we closed
            case "closed":
                if issue.closed_by.login in developer_ids \
                        and issue.updated_at >= report_start_date:
                    report_issues.append(
                        tuple(
                            (
                                f"{issue.closed_at}",
                                "Issue",
                                "closed",
                                f"{branch_name.rjust(6)}",
                                f"{issue.url}",
                                f"{issue.title}",
                            )
                        )
                    )
        return report_issues


if __name__ == "__main__":
    filtered_issues = filter_issues(all_issues)

    results = format_issues(filtered_issues)

    for line in results:
        print(line)


