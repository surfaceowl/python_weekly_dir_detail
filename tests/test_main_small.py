"""
test integrated PR and issues with short list of inputs for testing
"""
import logging

from config import end_date_buffer
from config import issues_all
from utilities import check_github_rate_limit
from weekly_issues_summary import get_final_issues

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def test_main():
    check_github_rate_limit()

    from config import pull_requests_all
    from config import start_date
    from config import end_date
    from config import developer_ids
    from weekly_pr_summary import get_prs_from_list_pr_numbers
    from weekly_pr_summary import get_prs_from_date_range
    from weekly_pr_summary import extract_pr_info_to_final_format
    from weekly_pr_summary import sort_final_data
    from weekly_pr_summary import format_blog_html_block

    pr_obj_shortlist, pr_reviewed = get_prs_from_list_pr_numbers(
        [29653, 29664, 13580, 28722], developer_ids, start_date, end_date
    )

    pr_raw_results = extract_pr_info_to_final_format(
        pr_obj_shortlist, pr_reviewed, developer_ids, start_date, end_date
    )

    pr_sorted_results = sort_final_data(pr_raw_results)

    pr_final_results = format_blog_html_block(pr_sorted_results)

    issue_final_results = get_final_issues(
        issues_all, developer_ids, start_date, end_date, end_date_buffer
    )

    issue_final_results = issue_final_results[:5]

    combined_results = pr_final_results + issue_final_results

    combined_results = sort_final_data(combined_results)

    for item in combined_results:
        print(item)

    assert True
