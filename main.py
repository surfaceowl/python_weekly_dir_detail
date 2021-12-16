"""
main file to configure and execute GitHub searches to summarize
PR and Issue data for Developer In Residence blog
"""
import logging

from utilities import check_github_rate_limit
from weekly_pr_summary import get_final_summary
from weekly_pr_summary import sort_final_data
from weekly_issues_summary import get_final_issues
from config import developer_ids
from config import start_date
from config import end_date
from config import end_date_buffer
from config import pull_requests_all
from config import issues_all

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def main():
    check_github_rate_limit()
    pr_results = get_final_summary(
        pull_requests_all, developer_ids, start_date, end_date
    )

    issue_results = get_final_issues(
        issues_all, developer_ids, start_date, end_date, end_date_buffer
    )

    combined_results = pr_results + issue_results

    # combined_results = sort_final_data(combined_results)

    for item in combined_results:
        print(item)


if __name__ == "__main__":

    main()
