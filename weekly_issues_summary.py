"""
module to pull select issue data from GitHub for cpython Developer In Residence weekly 
"""
import datetime
import logging

from config import developer_ids
from config import end_date
from config import issues_all
from config import start_date

logging.basicConfig(encoding="utf-8", level=logging.WARNING)


def filter_issues(input_issues):
    """
    filter and sort issues and prs
    :param input_issues:
    :return: list of combined issues
    """
    logging.info("begin filter_issues")
    issues_opened, issues_closed, issued_combined = [], [], []

    for issue in input_issues:
        # simplify condition names
        if issue.last_modified is None:
            date_to_consider = issue.created_at
        else:
            date_to_consider = issue.last_modified

        interesting_date_range = bool(
            start_date <= date_to_consider <= (end_date + datetime.timedelta(days=1))
        )

        interesting_owner = bool(issue.user.login in developer_ids)

        if issue.closed_by is None:
            interesting_closer = False
        else:
            interesting_closer = bool(issue.closed_by.login in developer_ids)

        # filter stuff we want to keep
        if interesting_date_range:
            if issue.state == "closed" and (interesting_owner or interesting_closer):
                issues_opened.append(issue)
            elif issue.state == "open" and interesting_owner:
                issues_opened.append(issue)
            else:
                continue

    issues_combined = sorted(issues_opened + issues_closed, key=lambda x: x.updated_at)

    return issues_combined


def format_issues(input_issues):
    """
    extract and formats key fields into an output list.
    :param: input_issues: list of tuples containing issues of interest
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
                if issue.user.login in developer_ids and issue.updated_at >= start_date:
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


if __name__ == "__main__":
    filtered_issues = filter_issues(issues_all)

    results = format_issues(filtered_issues)

    for line in results:
        print(line)
