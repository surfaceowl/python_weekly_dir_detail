# type: ignore
"""
module to pull select issue data from GitHub for cpython Developer In Residence weekly 
"""
import datetime
import logging
import typing

import github

from config import repo

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def check_if_issue_date_interesting(
    date_to_consider: datetime.datetime,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    end_date_buffer: int = 0,
) -> bool:
    """checks dates on a PR object to determine if date should be used as a filter

    Args:
      date_to_consider: datetime object
      start_date: beginning of filter period
      end_date: end of filter period
      end_date_buffer: optional buffer to extend end date, and help capture
    issues closed by others after the DIR work period

    Returns:
      tuple: True/False if datetime field is interesting as a filter
      date_to_consider: datetime.datetime:
      start_date: datetime.datetime:
      end_date: datetime.datetime:
      end_date_buffer: int:  (Default value = 0)

    """

    return bool(
        start_date
        <= date_to_consider
        <= (end_date + datetime.timedelta(days=int(end_date_buffer)))
    )


def get_issues(start_date_inner: datetime.datetime):
    """use PyGithub API to return issues in descending order
    from most recently updated to older, stopping at the oldest date = start date

    Args:
      start_date_inner: date we stop getting issues from GitHub

    Returns:
      GitHub PaginatedList, list of tuples containing PR objects from GitHub
      start_date_inner: datetime.datetime:

    """

    logging.info("begin pulling issues of interest")
    return repo.get_issues(
        state="all", since=start_date_inner, sort="updated", direction="desc"
    )


# noinspection PyUnresolvedReferences,GrazieInspection
def filter_issues(
    input_issues: github.PaginatedList.PaginatedList,
    developer_ids: list,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    end_date_buffer: int = 0,
) -> list:
    """filter issues by various parameters, sorted to help debugging

    Args:
      input_issues: issues (tuples) from GitHub
      developer_ids: GitHub id strings to filter
      start_date: for issue filtering
      end_date: for issue filtering
      end_date_buffer: optional buffer to extend end date to capture issues
    closed by others after the specific period we care about; set in config.py

    Returns:
      list of combined and sorted issues

    """
    logging.info("begin filter_issues")
    issues_opened, issues_closed, issued_combined = [], [], []

    for issue in input_issues:
        # simplify condition names
        if issue.last_modified is None:
            date_to_consider = issue.created_at
        else:
            date_to_consider = issue.last_modified

        interesting_date_range = check_if_issue_date_interesting(
            date_to_consider, start_date, end_date, end_date_buffer
        )

        # filter stuff we want to keep
        if interesting_date_range:
            interesting_issue_owner = (
                False
                if issue.user.login is None
                else bool(issue.user.login in developer_ids)
            )

            interesting_issue_closer = (
                False
                if issue.closed_by is None
                else bool(issue.closed_by.login in developer_ids)
            )

            if issue.state == "closed" and (
                interesting_issue_owner or interesting_issue_closer
            ):
                issues_opened.append(issue)
            elif issue.state == "open" and interesting_issue_owner:
                issues_opened.append(issue)
            else:
                continue

    return sorted(issues_opened + issues_closed, key=lambda x: x.updated_at)


@typing.no_type_check
def format_issues(
    input_issues: list,
    developer_ids: list,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    end_date_buffer: int = 0,
) -> list:
    """extract and formats key fields into an output list

    Args:
      input_issues: issues (tuples) from GitHub
      developer_ids: GitHub id strings to filter
      start_date: start date of report
      end_date: similar, passed in for testing
      end_date_buffer: number of days to add to 'end time'

    Returns:
      list issues_summary: list of tuples with select, reformatted fields

    """
    logging.info("beginning format issues")
    issues_summary = []

    len(input_issues)

    for issue in input_issues:

        # determine branch based on common PR naming pattern with [X.Y] branch prefix
        if "[main]" in issue.title or "[3." not in issue.title:
            branch_name = "[main]"
        else:
            branch_name = str(issue.title).split(" ", 2)[0]

        match issue.state:
            case "open":
                # issues we authored
                if (
                    issue.user.login in developer_ids
                    and check_if_issue_date_interesting(
                        issue.updated_at, start_date, end_date, end_date_buffer
                    )
                ):
                    issues_summary.append(
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

            # issues we closed
            case "closed":
                if issue.closed_by.login in developer_ids:
                    issues_summary.append(
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
        # END match
    # END for issue in input_issues

    return issues_summary


def get_final_issues(
    issues_all: list,
    developer_ids: list,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    end_date_buffer: int = 0,
) -> list:
    """convenience function to wrap getting, filtering and formatting issues
    to mirror functions in weekly_pr_summary

    Args:
      issues_all: issues (tuples) from GitHub
      developer_ids: GitHub id strings to filter
      start_date: beginning of reporting period
      end_date: end of reporting period
      end_date_buffer: optional buffer to extend reporting period

    Returns: list of formatted strings; by calling the `format_issues` function

    """

    filtered_issues = filter_issues(
        issues_all, developer_ids, start_date, end_date, end_date_buffer
    )

    return format_issues(
        filtered_issues, developer_ids, start_date, end_date, end_date_buffer
    )
