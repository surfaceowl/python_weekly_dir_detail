import os
from github import Github
import subprocess
import datetime

testdate_str = "2021-12-02"
testdate = datetime.date.fromisoformat(testdate_str)
day_of_week = testdate.strftime("%A")

print(testdate_str, testdate, day_of_week)


github_host = Github(os.environ.get("GITHUB_ACCESS_TOKEN"))
repo = github_host.get_repo("python/cpython")

names = [repo.name for repo in github_host.get_user().get_repos()]
for idx, name in enumerate(sorted(names)):
    print(f"{idx:>5}  {name}")

print([branch for branch in list(repo.get_branches())])
