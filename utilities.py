"""
general project utilities
"""
import datetime
import logging
from time import time

from config import github_host

logging.basicConfig(encoding="utf-8", level=logging.WARNING)


def check_github_rate_limit():
    github_ratelimit = github_host.get_rate_limit()
    logging.debug(f"github ratelimit status is: {github_ratelimit}")
    return github_ratelimit


def create_date_object(input_standard_date_string):
    """given input string of form YYYY-MM-DD HH:MM:SS; convert to datetime object"""
    return datetime.datetime.strptime(input_standard_date_string, "%Y-%m-%d %H:%M:%S")


def date_interesting(pr_datetime_object) -> bool:
    """
    :param pr_datetime_object
    if this date is interesting must check for None first,
    since closed and merge fields are not populated
    also added buffer for PRs updated after review by others"""

    if pr_datetime_object is None:
        is_date_interesting = False
    else:
        is_date_interesting = bool(
            report_start_date
            <= pr_datetime_object
            <= (report_end_date + datetime.timedelta(days=3))
        )
    return is_date_interesting


def timer_decorator(function):
    # This function shows the execution time of
    # the function object passed
    def wrapped_function(*args, **kwargs):
        time_start = time()
        result = function(*args, **kwargs)
        time_done = time()
        logging.info(
            f"function {function.__name__!r} executed in"
            f" {(time_done - time_start):.1f}s"
        )
        return result

    return wrapped_function


def is_date_interesting(report_start_date, report_end_date, pr_datetime_object):
    """
    :param pr_datetime_object
    if this date is interesting must check for None first,
    since closed and merge fields are not populated
    also added buffer for PRs updated after review by others"""

    if pr_datetime_object is None:
        return False
    else:
        is_date_interesting = bool(
            report_start_date
            <= pr_datetime_object
            <= (report_end_date + datetime.timedelta(days=3))
        )
    return is_date_interesting
