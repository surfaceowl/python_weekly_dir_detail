"""
main file to configure and execute GitHub searches to summarize
PR and Issue data for Developer In Residence blog
"""
import logging

from config import developer_ids
from config import end_date
from config import end_date_buffer
from config import issues_all
from config import pull_requests_all
from config import start_date
from utilities import check_github_rate_limit
from utilities import timer_decorator
from weekly_issues_summary import get_final_issues
from weekly_pr_summary import format_final_html_block
from weekly_pr_summary import get_final_summary
from weekly_pr_summary import sort_final_data

logging.basicConfig(encoding="utf-8", level=logging.INFO)


@timer_decorator
def main():
    """main program to pull data and produce blog-ready output"""
    check_github_rate_limit()

    # threading may help speed up due to lots of I/O with GitHub
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        prs = executor.submit(
            get_final_summary,
            pull_requests_all,
            developer_ids,
            start_date,
            end_date
        )

        issues = executor.submit(
            get_final_issues,
            issues_all,
            developer_ids,
            start_date,
            end_date,
            end_date_buffer,
        )

    combined_results = prs.result() + issues.result()

    combined_results = sort_final_data(combined_results)

    combined_results = format_final_html_block(combined_results)

    # write to local file for convenience & persistence
    with open("GitHub_summary.txt", "wb") as writer:
        for item in combined_results:
            writer.write(f"{item}\n".encode())

    return True


if __name__ == "__main__":
    """before you execute this - please modify search parameters in config.py"""
    main()
