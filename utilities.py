"""
general project utilities
"""
import datetime
import logging
import os
import hashlib
from time import time

from config import github_host

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def check_github_rate_limit():
    github_ratelimit = github_host.get_rate_limit()
    logging.debug(f"GitHub ratelimit status is: {github_ratelimit}")
    return github_ratelimit


def create_date_object(input_standard_date: str) -> datetime:
    """given input string of form YYYY-MM-DD HH:MM:SS; convert to datetime object"""
    return datetime.datetime.strptime(input_standard_date, "%Y-%m-%d %H:%M:%S")


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


def hash_file(filename):
    if os.path.isfile(filename) is False:
        raise Exception("File not found for hash operation")

    # open file for reading in binary mode
    with open(filename, "rb") as file:
        return hashlib.sha512(file.read()).hexdigest()
