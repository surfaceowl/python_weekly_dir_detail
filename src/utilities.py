"""
general project utilities
"""
import datetime
import hashlib
import logging
import os
from time import time

from github import GithubException
from github import RateLimitExceededException

from config import github_host

logging.basicConfig(encoding="utf-8", level=logging.INFO)


def check_github_rate_limit():
    """check current consumption of 5,000 call/hour rate limit for
    authenticated GitHub user tokens

    Args: None

    Returns:
        Tuple of current API calls (within hour); total hourly API calls, API reset time
    """

    github_ratelimit: int = 5000

    try:
        github_ratelimit = github_host.get_rate_limit()
    except RateLimitExceededException:
        logging.error(f"GitHub API rate limit exceeded: {github_ratelimit}")
    except GithubException:
        logging.error(f"Another GitHub API error occurred: {GithubException}")
    finally:
        logging.info(f"GitHub ratelimit status is: {github_ratelimit}")

    return github_ratelimit


def create_date_object(input_standard_date: str):
    """given input string of form YYYY-MM-DD HH:MM:SS; convert to datetime object

    Args:
      input_standard_date: input string in specific standard format returned by GitHub

    Returns:
        datetime.datetime object representing same time as input string

    """
    return datetime.datetime.strptime(input_standard_date, "%Y-%m-%d %H:%M:%S")


def timer_decorator(function):
    """
    timer decorator to track elapsed runtime for functions

    Args:
      function: arbitrary function we want to track elapsed runtime of

    Returns:
        wrapped function

    """
    # This function shows the execution time of
    # the function object passed
    def wrapped_function(*args, **kwargs):
        """
        wrapped function for timer decorator
        """
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
    """
    computes hash value of file contents, to simplify pytest assert statements for
    complex test cases that output files.  For cross-platform compatibility, make sure
    files are read/written in binary, and use unix-style line endings, otherwise hashes
    will not match despite content being same in ASCII.

    Args:
        filename

    Returns:
        hashnumber

    """
    if os.path.isfile(filename) is False:
        raise Exception("File not found for hash operation")

    # open file for reading in binary mode
    with open(filename, "rb") as file:
        return hashlib.sha512(file.read()).hexdigest()
