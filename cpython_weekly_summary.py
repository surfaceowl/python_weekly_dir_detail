# script to pull select data from GitHub for cpython Developer In Residence
# weekly reporting.
# collect final results in a list, to make html ready lines to drop into the weekly blog
# requires env var:  GITHUB_ACCESS_TOKEN, a valid access token from your GitHub account
import datetime
import logging
import os
from time import time
import requests

import github.GithubException
from github import Github

# setup search parameters
github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))  # must be set in env var
repo = github_host.get_repo("python/cpython")  # target repo
developer_ids = ["ambv"]  # list in case you want more than one
report_start_date = datetime.datetime(2021, 8, 30)  # change this 11/15
report_end_date = datetime.datetime(2021, 9, 5)  # change this  11/21

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
    :return: pull_requests_of_interest; list of tuples - all PR detail
    :return: reviewed_pull_requests; list of ints; PR numbers that were reviewed only
    """

    def developer_wrote_comments(pr_number):
        """
        PyGitHub does not provide easy way to confirm if a developer reviewed a PR, so
        we will parse the text written comments by target developer_id
        :param pr_number: pull request id number
        :return: bool: developer_commented
        """
        developer_commented = False
        target = (
            f"https://api.github.com/repos/python/cpython/issues/"
            f"{pr_number}/comments"
        )
        response = requests.get(target).text
        for developer in developer_ids:
            if developer in response:
                developer_commented = True
                break
        return developer_commented

    # setup
    logging.info(f"github ratelimit status is: {github_ratelimit}")
    pull_requests_of_interest = []
    pull_requests_reviewed_inner = []
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
                # PR's we closed
                if (
                    each_pull_request.state == "closed"
                    and report_start_date
                    <= each_pull_request.merged_at
                    <= report_end_date
                    and each_pull_request.merged_by.login in developer_ids
                ):
                    pull_requests_of_interest.append(each_pull_request)

                # PRs we authored
                elif (
                    each_pull_request.state == "open"
                    and report_start_date
                    <= each_pull_request.updated_at
                    <= report_end_date
                    and each_pull_request.user in developer_ids
                ):
                    pull_requests_of_interest.append(each_pull_request)

                # get PRs we reviewed by parsing pull comments by developer_id
                # requires returning separate list of 'reviewed' PRs, so
                # we don't have to process again
                elif (
                    each_pull_request.state == "open"
                    and report_start_date
                    <= each_pull_request.updated_at
                    <= report_end_date
                    and each_pull_request.comments >= 1  # defer expensive requests call
                ):
                    if developer_wrote_comments(each_pull_request.number) is True:
                        pull_requests_of_interest.append(each_pull_request)
                        pull_requests_reviewed_inner.append(each_pull_request.number)

    print("\n")
    print("PRs reviewed / found through comments search")
    for item in pull_requests_reviewed_inner:
        print(item)
    return pull_requests_of_interest, pull_requests_reviewed_inner


@timer_decorator
def extract_friendly_report_info(interesting_pull_requests, reviewed_pull_requests):
    """
    extracts and formats key fields into copy/paste ready text block
    to drop into the weekly blog report
    :param interesting_pull_requests: list of tuples, subset of PRs we care about
    :param reviewed_pull_requests: list of ints, PR #s confirmed by comment text
    :return: report_data; list of lists we can easily print
    """
    report_data = []
    for each_pull_request in interesting_pull_requests:

        # compute current_pr_action
        current_pr_action = None

        if (
            each_pull_request.merged_at is None
            and each_pull_request.user.login in developer_ids
            and each_pull_request.created_at >= report_start_date
        ):
            current_pr_action = "authored"

        elif each_pull_request.number in reviewed_pull_requests:
            current_pr_action = "reviewed"

        elif (
            report_start_date <= each_pull_request.merged_at <= report_end_date
            and each_pull_request.merged_by.login in developer_ids
        ):
            current_pr_action = "closed"

        # create concise text and HTML link for this PR
        link_text = f"{current_pr_action} GH-{each_pull_request.number}"

        # use html_url attribute for human friendly link,
        link_url = f"<a href={each_pull_request.html_url}>{link_text}</a>"

        # create friendly PR title for blog; trap for missing data
        if each_pull_request.base.ref is None:
            friendly_title = each_pull_request.title

        # add python version to title if not there already
        elif each_pull_request.base.ref not in each_pull_request.title:
            friendly_title = f"[{each_pull_request.base.ref}] {each_pull_request.title}"

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
                    current_pr_action,
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
            sorted(report_data, key=lambda key3: key3[3], reverse=True),
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
        final_url = report_item[4]
        draft_title = report_item[5]

        # insert section row for each time the day changes
        if current_day != last_day_used:
            report_output.append("")
            report_output.append(f"{current_day.strftime('%A')}")
            last_day_used = current_day

        # insert section row each time the work product changes
        if current_work_product != last_work_product_used:
            report_output.append("")
            report_output.append(f"{current_work_product}")
            last_work_product_used = current_work_product

        # check spacing in item title, so branch names line up neatly
        # fixes branch names <= [3.9]; [main], [3.10] and beyond have same len()
        if report_item[5][5] != "]":
            final_title = draft_title.rjust(len(draft_title) + 1)
        else:
            final_title = draft_title

        report_output.append(f"<li> {final_url} {final_title}/li>")

    # END for loop - add blank line at end of table
    report_output.append("")

    return report_output


# merge results for different sets of pull requests
# for pull_request_group in pull_requests_all:
try:
    pull_reports_we_care_about, pull_requests_reviewed = get_pull_requests_of_interest(
        pull_requests_all
    )
    final_summary = extract_friendly_report_info(
        pull_reports_we_care_about, pull_requests_reviewed
    )
except github.RateLimitExceededException:
    logging.error(f"github rate limit exceeded", github.RateLimitExceededException)
except github.GithubException as error:
    logging.error(f"a server error occurred {error}")
except IndexError as error:
    logging.error(error)

logging.info(f"github ratelimit status is: {github_ratelimit}")

# nice formatting
final_summary = format_blog_html_block(final_summary)

for item in final_summary:
    print(item)  # cut the branch name from prefix to mirror current blog format


print(f"github ratelimit status is: {github_ratelimit}")
