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
    logging.info(f"github ratelimit status is: {github_ratelimit}")
    return github_ratelimit


def create_date_object(input_standard_date_string):
    """given input string of form YYYY-MM-DD HH:MM:SS; convert to datetime object"""
    return datetime.datetime.strptime(input_standard_date_string, "%Y-%m-%d %H:%M:%S")


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
