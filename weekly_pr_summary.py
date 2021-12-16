"""
module pulls select PR data from GitHub for cpython Developer In Residence reporting.
Collect final results in a list of html lines ready to drop into the weekly blog
requires env var:  GITHUB_ACCESS_TOKEN, a valid access token from your GitHub account
"""
import datetime
import logging
import re

import github.GithubException
import requests

from config import github_token
from config import buildbot_ids
from config import end_date_buffer
from config import repo
from utilities import timer_decorator

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def developer_wrote_comments(pr_object, developer_ids) -> bool:
    """
    PyGitHub does not provide easy way to confirm if a developer reviewed a PR.
    As workaround, we parse written PR comments for target developer_id
    assuming if "{developer_id} approved these changes" is found, the PR was reviewed
    :param pr_object:
    :param developer_ids: list of GitHub IDs of developers we are interested in
    :return: bool: developer_commented
    """
    # use our person GitHub access token to avoid response limits
    headers_for_requests = {"Authorization": f"token {github_token}"}
    pr_url = requests.get(pr_object.url, headers=headers_for_requests).text
    pr_html_url = requests.get(pr_object.html_url, headers=headers_for_requests).text
    pr_comments_url = requests.get(
        pr_object.review_comments_url, headers=headers_for_requests
    ).text
    pr_discussion_text = pr_url + pr_html_url + pr_comments_url
    reviewed_search_string = "approved these changes"
    commented_search_string_1 = "left a comment"
    commented_search_string_2 = "commented"
    commented_search_string_3 = "closed this"

    search_strings = [
        reviewed_search_string,
        commented_search_string_1,
        commented_search_string_2,
        commented_search_string_3,
    ]

    found_string = False
    successful_searches = []

    for developer in developer_ids:
        for string in search_strings:
            new_string = f"{developer} {string}"
            # python in search
            # logging.warning(f"searching exact string: {new_string}")
            if new_string in pr_discussion_text:
                successful_searches.append((f"found! with exact string: {new_string}"))
                # logging.warning(f"found! exact string: {new_string}")
                # return True

    for developer in developer_ids:
        for string in search_strings:
            # regex finds {developer} NEAR {search string} (ref: https://regex101.com/)
            regex = fr"\b({developer})\W+(?:\w+\W+){0,3}?({string})\b"
            pattern = re.compile(regex)
            # logging.warning(f"searching {string} with {regex}")
            if re.search(pattern, pr_discussion_text):
                successful_searches.append(f"found!  with {regex}")
                # logging.warning(f"found!  searching {string} with {regex}")
                # return True

    if not successful_searches:
        return False
    number_of_successful_searches = len(successful_searches)
    successful_searches.insert(0, f"{pr_object.number}")
    successful_searches.insert(1, number_of_successful_searches)
    for item in successful_searches:
        logging.warning(item)
    return True


@timer_decorator
def get_prs_from_list_pr_numbers(input_list, developer_ids, start_date, end_date):
    """retrieves list of pr objects from arbitrary list of GitHub pr numbers
    useful for quickly getting summary info manually"""
    logging.info(f"retrieving {len(input_list)} PRs: {input_list}")

    prs_to_summarize = [repo.get_pull(item) for item in sorted(input_list)]

    pull_requests_of_interests, pull_requests_reviewed = get_prs_from_date_range(
        prs_to_summarize, developer_ids, start_date, end_date
    )
    return pull_requests_of_interests, pull_requests_reviewed


@timer_decorator
def get_prs_from_date_range(
    pull_request_inputs, developer_ids, report_start_date, report_end_date
):
    """
    filters all PRs in the repo for the one's we care about
    driven by repo name; developer ids of interest and start/end dates
    :param pull_request_inputs: paginated list of all PRs from GitHub API
    :param developer_ids: list to drive search results
    :param report_start_date: for local filtering
    :param report_end_date: also for local filtering
    :return: pull_requests_of_interest; list of tuples - all PR detail
    :return: reviewed_pull_requests; list of ints; PR numbers that were reviewed
    """
    logging.info("begin finding pull requests of interest.")

    # setup
    # add buffer to end date to capture changes by bots after DIR approval in period
    report_end_date = report_end_date + datetime.timedelta(days=end_date_buffer)
    pull_requests_of_interest = []
    pull_requests_reviewed_inner = []

    for each_pull_request in pull_request_inputs:

        logging.warning(f"checking PR# {each_pull_request.number}")

        if each_pull_request.updated_at < report_start_date:
            # Our API call return is sorted in descending dates, once we go earlier
            # than report_start_date, break out of loop to reduce # of API calls
            break

        date_check_results = check_for_interesting_dates(
            each_pull_request, report_end_date, report_start_date
        )
        created_date_of_interest = date_check_results.get("created")
        updated_date_of_interest = date_check_results.get("updated")
        closed_date_of_interest = date_check_results.get("closed")
        merged_date_of_interest = date_check_results.get("merged")
        dev_comments = developer_wrote_comments(each_pull_request, developer_ids)

        # keep PR's we merged and PRs we own that are merged by bots
        if (
            each_pull_request.merged is True
            and merged_date_of_interest is True
            and each_pull_request.state == "closed"
            and bool(
                bool(each_pull_request.merged_by.login in developer_ids)
                or bool(
                    each_pull_request.user.login in developer_ids
                    and each_pull_request.merged_by.login in buildbot_ids
                )
            )
        ):
            pull_requests_of_interest.append(each_pull_request)
            if developer_wrote_comments(each_pull_request, developer_ids) is True:
                pull_requests_reviewed_inner.append(each_pull_request.number)
                # logging.warning(f"added PR: {each_pull_request.number}  merged")

        # keep PRs we authored
        if created_date_of_interest and each_pull_request.user.login in developer_ids:
            pull_requests_of_interest.append(each_pull_request)
            # logging.warning(f"added PR: {each_pull_request.number}  authored")

        # keep PRs we reviewed
        if (
            updated_date_of_interest
            and each_pull_request.comments >= 1
            and dev_comments is True
        ):
            pull_requests_of_interest.append(each_pull_request)
            pull_requests_reviewed_inner.append(each_pull_request.number)
            # logging.warning(f"added PR: {each_pull_request.number}  reviewed")

            # keep PRs we closed or enabled another to close (do not use merged filter)
            if each_pull_request.state == "closed" and closed_date_of_interest:
                pull_requests_of_interest.append(each_pull_request)
                # logging.warning(f"added PR: {each_pull_request.number}  closed")
            else:
                # logging.warning(
                #     f"did NOT add PR: {each_pull_request.number}  no action"
                # )
                continue

    return pull_requests_of_interest, pull_requests_reviewed_inner


# END get_prs_from_date_range


@timer_decorator
def extract_pr_info_to_final_format(
    interesting_pull_requests,
    reviewed_pull_requests,
    developer_ids,
    report_start_date,
    report_end_date,
):
    """
    this function extracts and formats key fields into copy/paste ready text block
    to drop into the weekly blog report
    assumes PRs may have multiple reportable states and dates in each period
    e.g., authored & merged, reviewed & closed, etc. too many to list
    :param interesting_pull_requests: list of tuples, subset of PRs we care about
    :param reviewed_pull_requests: list of ints, PR #s confirmed by comment text
    :param developer_ids: list of developer ids we are interested in
    :param report_start_date: beginning of reporting period for local filtering
    :param report_end_date: end of reporting period for local filtering
    :return: report_data; list of lists we can easily print
    """
    logging.info("begin extracting PR info into friendly report format")

    report_data = []
    for each_pull_request in interesting_pull_requests:

        date_check_results = check_for_interesting_dates(
            each_pull_request, report_end_date, report_start_date
        )
        created_date_of_interest = date_check_results.get("created")
        updated_date_of_interest = date_check_results.get("updated")
        closed_date_of_interest = date_check_results.get("closed")
        merged_date_of_interest = date_check_results.get("merged")

        # check each PR for key state changes during reporting period
        # merged - by DIR of interest
        if (
            each_pull_request.state == "closed"
            and closed_date_of_interest is True
            and each_pull_request.merged is True
            and merged_date_of_interest is True
        ):
            current_pr_action = "merged"
            date_to_use_for_pr = each_pull_request.merged_at
            report_data = report_data_append(
                report_data, each_pull_request, current_pr_action, date_to_use_for_pr
            )

        # authored, does not depend on pr state
        if (
            each_pull_request.user.login in developer_ids
            and created_date_of_interest is True
        ):
            current_pr_action = "authored"
            date_to_use_for_pr = each_pull_request.updated_at
            report_data = report_data_append(
                report_data, each_pull_request, current_pr_action, date_to_use_for_pr
            )

        # closed - captures PRs closed but not merged
        # no strict ID that DIR closed in object
        # TODO: check closed not merged criteria with `ambv`
        if closed_date_of_interest is True and each_pull_request.merged is False:
            current_pr_action = "closed"
            date_to_use_for_pr = each_pull_request.closed_at
            report_data = report_data_append(
                report_data, each_pull_request, current_pr_action, date_to_use_for_pr
            )

        # reviewed PR - identified in `reviewed_pull_requests` list
        if (
            each_pull_request.number in reviewed_pull_requests
            and updated_date_of_interest is True
        ):
            current_pr_action = "reviewed"
            date_to_use_for_pr = each_pull_request.updated_at
            report_data = report_data_append(
                report_data, each_pull_request, current_pr_action, date_to_use_for_pr
            )

        else:
            continue

    return report_data


def check_for_interesting_dates(
    each_pull_request, report_end_date, report_start_date
) -> dict:
    """converts select datetime fields to boolean; simplifies PR classification logic"""
    created_date_of_interest = bool(
        report_start_date <= each_pull_request.created_at <= report_end_date
    )

    updated_date_of_interest = bool(
        report_start_date <= each_pull_request.updated_at <= report_end_date
    )
    if each_pull_request.closed_at is not None:
        closed_date_of_interest = bool(
            report_start_date <= each_pull_request.closed_at <= report_end_date
        )
    else:
        closed_date_of_interest = False

    if each_pull_request.merged_at is not None:
        merged_date_of_interest = bool(
            report_start_date <= each_pull_request.merged_at <= report_end_date
        )
    else:
        merged_date_of_interest = False
    return {
        "created": created_date_of_interest,
        "updated": updated_date_of_interest,
        "closed": closed_date_of_interest,
        "merged": merged_date_of_interest,
    }


# END extract_pr_info_to_final_format


def report_data_append(
    report_data, each_pull_request, current_pr_action, date_to_use_for_pr
):
    """adds confirmed pr event to the report_data list"""
    # create concise text and HTML link
    link_text = f"{current_pr_action} GH-{each_pull_request.number}"
    link_url = f"<a href={each_pull_request.html_url}>{link_text}</a>"
    friendly_title = pr_create_friendly_title(each_pull_request)
    report_data.append(
        tuple(
            (
                f"{date_to_use_for_pr}",
                "PR",
                current_pr_action,
                f"{each_pull_request.base.ref:>6}",
                f"{link_url}",
                f"{friendly_title}",
            )
        )
    )

    return report_data


def pr_create_friendly_title(each_pull_request) -> str:
    """create friendly PR title for blog
    :param each_pull_request: pr object
    :return friendly_title: cleaned up title string"""
    if (
        each_pull_request.base.ref is None
        or each_pull_request.base.ref in each_pull_request.title
    ):
        friendly_title = each_pull_request.title
    else:
        friendly_title = f"[{each_pull_request.base.ref}] {each_pull_request.title}"
    github_pr_tag = f"(GH-{each_pull_request.number})"
    if github_pr_tag in friendly_title:
        friendly_title.replace(github_pr_tag, "")
    return friendly_title


def sort_final_data(report_data):
    # messy nested sort worth it for easy copy & paste output
    # outer sort = day of week (ascending)
    # 2nd sort = issue/PR (ascending)
    # inner sort = branch name (descending)
    logging.info("begin sort of final report")
    try:
        report_data = sorted(
            sorted(
                sorted(report_data, key=lambda key3: key3[3], reverse=True),
                key=lambda key1: key1[1],
            ),
            key=lambda key0: datetime.datetime.fromisoformat(key0[0]).date(),
        )
    except ValueError:
        pass

    return report_data


@timer_decorator
def format_blog_html_block(report_data):
    """
    create html block to mirror existing blog format for `Detailed Log` section
    bullet list sorted by Day of Week; category of work done (e.g., Issue/PR), then item
    :param report_data: list of tuples of input data
    :return: report_output: list of lists, ready for manual copy/paste into blog
    """
    logging.info("begin formatting for blog")
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


def get_final_summary(pull_requests, developer_ids, start_date, end_date):
    """
    utility to safely wrap our functions and return nicely summarized results
    :param developer_ids:
    :param pull_requests:  input list of pull request tuples
    :param start_date:  beginning of reporting period for local filtering
    :param end_date: end of reporting period for local filtering
    :return:
    """
    logging.info("starting main routine - pulling from GitHub for report")
    final_summary = []

    try:
        (
            pull_reports_we_care_about,
            pull_requests_reviewed,
        ) = get_prs_from_date_range(pull_requests, developer_ids, start_date, end_date)

        summary = extract_pr_info_to_final_format(
            pull_reports_we_care_about,
            pull_requests_reviewed,
            developer_ids,
            start_date,
            end_date,
        )

        final_summary = format_blog_html_block(summary)

    except github.RateLimitExceededException:
        logging.error("github rate limit exceeded", github.RateLimitExceededException)
    except github.GithubException as error:
        logging.error(f"a server error occurred {error}")
    except IndexError as error:
        logging.error(error)

    for item in final_summary:
        logging.info(item)

    return final_summary
