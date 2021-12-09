"""test for basic environment setup"""
import os
from github import Github


def test_github_token_env_var_exists():
    """tests correctly named env var for GitHub access exists
    needed for higher API rate limit to run necessary queries vs large cpython repo
    """
    assert os.getenv("GITHUB_ACCESS_TOKEN") is not None


def test_anonymous_github_access_works():
    """tests that user can access GitHub with provided user auth token
    anonymous GitHub access limits queries to 60 per hour, vs 5,000 per hour with token
    """
    anonymous_rate = Github(os.environ.get("GITHUB_ACCESS_TOKEN")).rate_limiting[1]
    assert anonymous_rate == 60


def test_authenticated_github_access_works():
    """tests that user can access GitHub with provided user auth token
    anonymous GitHub access limits queries to 60 per hour, vs 5,000 per hour with token
    .rate_limiting attributed returns a tuple: (# remaining, # allowed) (
    """
    authenticated_rate = Github(os.environ.get("GITHUB_ACCESS_TOKEN")).rate_limiting[1]
    assert authenticated_rate == 5000

