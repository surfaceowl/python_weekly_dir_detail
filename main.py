"""
main file to configure and execute GitHub searches to summarize
PR and Issue data for Developer In Residence blog
"""
import logging

from utilities import check_github_rate_limit
from weekly_pr_summary import get_final_summary
from config import developer_ids
from config import start_date
from config import end_date
from config import pull_requests_all

logging.basicConfig(encoding="utf-8", level=logging.WARNING)


def main():
    check_github_rate_limit()
    results = get_final_summary(pull_requests_all, developer_ids, start_date, end_date)

    for item in results:
        print(item)

    check_github_rate_limit()


if __name__ == "__main__":
    main()
