"""
module to pull select issue data from GitHub for cpython Developer In Residence weekly 
"""
import datetime
import logging

from config import repo

logging.basicConfig(encoding="utf-8", level=logging.WARNING)


def is_issue_date_interesting(date_to_consider, start_date, end_date, end_date_buffer):
    """checks if date should be used as a filter
    :param date_to_consider: datetime object
    :param start_date: beginning of filter period
    :param end_date: end of filter period
    :param end_date_buffer: optional buffer to extend end date, and help capture
    issues closed by others after the DIR work period"""

    return bool(
        start_date
        <= date_to_consider
        <= (end_date + datetime.timedelta(days=int(end_date_buffer)))
    )


def get_issues_of_interest(start_date_inner):
    """use PyGithub API and return issues from recently updated to older"""
    return repo.get_issues(
        state="all", since=start_date_inner, sort="updated", direction="desc"
    )


# noinspection PyUnresolvedReferences
def filter_issues(input_issues, developer_ids, start_date, end_date, end_date_buffer):
    """
     filter and sort issues
     :param developer_ids:
     :param input_issues: list of issue objects from GitHub to filter
     :param start_date: for issue filtering
     :param end_date:  for issue filtering
     :return: list of combined issues
    :param end_date_buffer: optional buffer to extend end date
    """
    logging.info("begin filter_issues")
    issues_opened, issues_closed, issued_combined = [], [], []

    for issue in input_issues:
        # simplify condition names
        if issue.last_modified is None:
            date_to_consider = issue.created_at
        else:
            date_to_consider = issue.last_modified

        interesting_date_range = is_issue_date_interesting(
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


def format_issues(input_issues, developer_ids, start_date, end_date, end_date_buffer):
    """
    extract and formats key fields into an output list
    :param input_issues: list of tuples containing issues of interest
    :param developer_ids: list of developer ids, passed in for testing
    :param start_date: start date of report, passed in for testing
    :param end_date: similar, passed in for testing
    :param end_date_buffer:
    :return: list of tuples containing reformatted key output fields
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
                if issue.user.login in developer_ids and is_issue_date_interesting(
                    issue.updated_at, start_date, end_date, end_date_buffer
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


def get_final_issues(issues_all, developer_ids, start_date, end_date, end_date_buffer):
    """
    convenience function to wrap getting, filtering and formatting issues
    to mirror functions in weekly_pr_summary
    :param issues_all: list of tuples of issues
    :param developer_ids: list of ids to check
    :param start_date: datetime of beginning of reporting periods
    :param end_date: datetime of end of reporting period
    :param end_date_buffer: optional buffer to extend reporting period
    """

    filtered_issues = filter_issues(
        issues_all, developer_ids, start_date, end_date, end_date_buffer
    )

    return format_issues(
        filtered_issues, developer_ids, start_date, end_date, end_date_buffer
    )


if __name__ == "__main__":
    pass
