# script to pull select data from GitHub for cpython Developer In Residence
# weekly reporting.
# collect final results in a list, to make html ready lines to drop into the weekly blog
# requires env var:  GITHUB_ACCESS_TOKEN, a valid access token from your GitHub account
import datetime
import logging
import os
from time import time

import github.GithubException
from github import Github

# setup search parameters
github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))  # must be set in env var
repo = github_host.get_repo("python/cpython")  # target repo
developer_ids = ["ambv"]  # list in case you want more than one
report_start_date = datetime.datetime(2021, 11, 15)  # change this
report_end_date = datetime.datetime(2021, 11, 21)  # change this

logging.basicConfig(encoding="utf-8", level=logging.WARNING)
# no date filter on get_pulls() method yet; state inputs must be single string
# get all PRs, so we can capture closed, merged and reviewed together
# sort via updated in reverse order; so we can stop iterating over API and
# stay below our API rate limit
pull_requests_all = repo.get_pulls(state="all", sort="updated", direction="descending")
pull_reports_we_care_about = []
final_summary = []
github_ratelimit = github_host.get_rate_limit()


def timer_decorator(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        time_start = time()
        result = func(*args, **kwargs)
        time_done = time()
        print(f"function {func.__name__!r} executed in {(time_done - time_start):.4f}s")
        return result

    return wrap_func


def create_date_object(input_standard_date_string):
    """given input string of form YYYY-MM-DD HH:MM:SS; convert to datetime object"""
    return datetime.datetime.strptime(input_standard_date_string, "%Y-%m-%d %H:%M:%S")


@timer_decorator
def get_pull_requests_of_interest(pull_request_inputs):
    """
    filters all PRs in the repo for the one's we care about
    driven by repo name; developer ids of interest and start/end dates
    :param pull_request_inputs:
    :return: pull_requests_of_interest; list of tuples
    """
    print(f"github ratelimit status is: {github_ratelimit}")

    pull_requests_of_interest = []
    pull_processed_counter = 0
    for each_pull_request in pull_request_inputs:
        if each_pull_request.updated_at < report_start_date:
            # since API return is sorted in reverse dates, once we go earlier
            # than report_start_date, break out of the loop to reduce # of API calls
            break
        else:
            pull_processed_counter += 1
            if each_pull_request.user.login is not None:
                user = each_pull_request.user.login
            else:
                user = each_pull_request.user
            if pull_processed_counter % 50 == 0:
                print(
                    f"{pull_processed_counter:>8,}  "
                    f"{each_pull_request.number:>6}  "
                    f"{each_pull_request.updated_at}  "
                    f"{user}  "
                )
            if (
                each_pull_request.merged_by is not None
                and each_pull_request.merged_at is not None
            ):
                # keep only PRs we are interested in
                if (
                    each_pull_request.state == "closed"
                    and each_pull_request.merged_by.login in developer_ids
                    and report_start_date
                    <= each_pull_request.merged_at
                    <= report_end_date
                ):
                    # TO DO: dump into list of dicts
                    pull_requests_of_interest.append(each_pull_request)

    return pull_requests_of_interest


@timer_decorator
def extract_friendly_report_info(pull_request_list):
    """
    extracts and formats key fields into copy/paste ready text block
    to drop into the weekly blog report
    :param pull_request_list: list of tuples, subset of PRs we care about
    :return: report_data; list of lists we can easily print
    """
    report_data = []
    for each_pull_request in pull_request_list:

        # create concise text and HTML link for this PR
        link_text = f"closed GH-{each_pull_request.number}"
        # use html_url attribute for human friendly link,
        # vs api link at url attribute
        link_url = f"<a href={each_pull_request.html_url}>{link_text}</a>"

        # create friendly PR title for blog; trap for missing data
        if each_pull_request.base.ref is None:
            friendly_title = each_pull_request.title

        elif each_pull_request.base.ref not in each_pull_request.title:
            # add python version to title if not there already
            friendly_title = (
                f"[{each_pull_request.base.ref}] {each_pull_request.title}"
            )

        else:
            friendly_title = each_pull_request.title

        potential_duplicate_pr_ref_num = f"(GH-{each_pull_request.number})"
        if potential_duplicate_pr_ref_num in friendly_title:
            friendly_title.replace(each_pull_request.number, "")

        report_data.append(
            tuple(
                (
                    f"{each_pull_request.merged_at}",
                    "PR",
                    f"{each_pull_request.base.ref:>6}",
                    f"{link_url}",
                    f"{friendly_title}",
                )
            )
        )

    # messy nested sort worth it for easy copy & paste output
    # outer sort = day of week (ascending)
    # 2nd sort = issue/PR (ascending)
    # inner sort = branch name (descending)
    report_data = sorted(
        sorted(
            sorted(report_data, key=lambda key2: key2[2], reverse=True),
            key=lambda key1: key1[1],
        ),
        key=lambda key0: datetime.datetime.fromisoformat(key0[0]).date(),
    )

    return report_data


@timer_decorator
def format_blog_html_block(report_data):
    """
    create html block to mirror existing blog format for `Detailed Log` section
    bullet list sorted by Day of Week; category of work done (e.g., Issue/PR), then item
    :param report_data: list of tuples of input data
    :return: report_output: list of lists, ready for manual copy/paste into blog
    """
    report_output = []
    last_day_used = None
    last_work_product_used = None

    for report_item in report_data:
        current_day = datetime.datetime.fromisoformat(report_item[0]).date()
        current_work_product = report_item[1]

        # insert section row for each time the day changes
        if current_day != last_day_used:
            report_output.append("")
            report_output.append(f"{current_day.strftime('%A')}")
            last_day_used = current_day

        # insert section row each time the word product changes
        if current_work_product != last_work_product_used:
            report_output.append("")
            report_output.append(f"{current_work_product}")
            last_work_product_used = current_work_product

        # check spacing in item title, so branch names line up neatly
        # fixes branch names <= [3.9]; [main], [3.10] and beyond have same len()
        if report_item[4][5] != "]":
            formatted_title = report_item[4].rjust(len(report_item[4]) + 1)
        else:
            formatted_title = report_item[4]

        report_output.append(f"<li> {report_item[3]} {formatted_title}/li>")

    # END for loop - add blank line at end of table
    report_output.append("")

    return report_output


# merge results for different sets of pull requests
# for pull_request_group in pull_requests_all:
try:
    pull_reports_we_care_about = get_pull_requests_of_interest(pull_requests_all)
except github.RateLimitExceededException:
    logging.error(f"github rate limit exceeded", github.RateLimitExceededException)
except github.GithubException as error:
    logging.error(f"a server error occurred {error}")

try:
    final_summary = extract_friendly_report_info(pull_reports_we_care_about)
except IndexError as error:
    logging.error(error)

print(f"github ratelimit status is: {github_ratelimit}")

# nice formatting
final_summary = format_blog_html_block(final_summary)

for item in final_summary:
    print(item)  # cut the branch name from prefix to mirror current blog format
