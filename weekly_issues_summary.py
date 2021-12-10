"""
module to pull select issue data from GitHub for cpython Developer In Residence weekly 
"""
import datetime
import dateutil.parser
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

    issues_opened = []
    issues_closed = []

    for issue in input_issues:
        if issue.state == "closed":
            if (
                issue.closed_by.login in developer_ids
                and start_date
                <= dateutil.parser.parse(issue.last_modified).replace(tzinfo=None)
                <= (end_date + datetime.timedelta(days=1))
            ):
                issues_closed.append(issue)
        else:
            if (
                issue.state == "open"
                and issue.user.login in developer_ids
                and start_date
                <= dateutil.parser.parse(issue.last_modified).replace(tzinfo=None)
                <= (end_date + datetime.timedelta(days=1))
            ):
                issues_opened.append(issue)

    combined_issues = sorted(issues_opened + issues_closed, key=lambda x: x.updated_at)

    return combined_issues


def format_issues(input_issues):
    """
    extract and formats key fields into an output list.
    :param: input_issues: list of tuples containing issues of interest
    :return: list of tuples containing reformatted key output fields
    """
    logging.info("beginning format issues")
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
                if issue.user.login in developer_ids and issue.updated_at >= start_date:
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
                if issue.user.login in developer_ids and issue.updated_at >= start_date:
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
                if (
                    issue.closed_by.login in developer_ids
                    and issue.updated_at >= start_date
                ):
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
    filtered_issues = filter_issues(issues_all)

    results = format_issues(filtered_issues)

    for line in results:
        print(line)
