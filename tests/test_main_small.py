"""
test integrated PR and issues with short list of inputs for testing
by testing hash values of actual vs expected results files, stored in ./tests
"""
import logging

from config import developer_ids
from config import end_date
from config import end_date_buffer
from config import issues_all
from config import start_date
from utilities import check_github_rate_limit
from utilities import hash_file
from weekly_issues_summary import get_final_issues
from weekly_pr_summary import extract_pr_info_to_final_format
from weekly_pr_summary import format_blog_html_block
from weekly_pr_summary import get_prs_from_list_pr_numbers
from weekly_pr_summary import sort_final_data

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def test_main():
    """ "test shadow copy of main routine with subset of data for end-to-end testing"""
    check_github_rate_limit()
    pr_obj_shortlist, pr_reviewed = get_prs_from_list_pr_numbers(
        [29653, 29664, 13580, 28722], developer_ids, start_date, end_date
    )

    pr_raw_results = extract_pr_info_to_final_format(
        pr_obj_shortlist, pr_reviewed, developer_ids, start_date, end_date
    )

    issue_raw_results = get_final_issues(
        issues_all, developer_ids, start_date, end_date, end_date_buffer
    )

    combined_results = pr_raw_results + issue_raw_results

    combined_results = sort_final_data(combined_results)

    combined_results = format_blog_html_block(combined_results)

    with open("test_main_small_test_results.txt", "wb") as writer:
        for item in combined_results:
            writer.write(f"{item}\n".encode())

    # test hash values of actual vs expected results
    actual_results = hash_file("test_main_small_test_results.txt")
    expected_results = hash_file("test_main_small_expected_output.txt")

    assert actual_results == expected_results
