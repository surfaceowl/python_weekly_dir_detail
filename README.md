<h2 align="center">Easy Formatted Summaries of GitHub Issue & PR progress</h2>

<p> "center">
<a href="https://github.com/psf/black/actions"><img alt="Actions Status" src="https://github.com/psf/black/workflows/Test/badge.svg"></a>
<a href="https://github.com/psf/black/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

> “Enter a few search parameters - get copy/paste ready summary of your issues 
> and PRs for your blog”

_GitHub Result Summary_ is a quick and dirty summaries of your GitHub issues and PR progress 
for periods of time you pick.  It adds titles and HTML links to your list of 
issues and PRs.  It captures all your major GitHub actions 
(e.g., open an issue, PR merge), for a repo you choose between two dates you choose.
In return, it gives you a sorted simple sorted list of accomplishments by day, 
with GitHub issue numbers, titles and HTML links.

Inspired by [Lukasz Langa's Weekly python Developer In Residence report](
https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/), _the output of GitHub 
Result Summary_ helps users quickly scan the list of accomplishments 
and understand what has been done by showing the title.  It helps maintainers by 
minimizing time required to summarize this info for interested users, by producing a 
block of text with links that can be dropped into a report or blog with minimal 
formatting.

There are some key differences, namely the GitHub Result Summary returns one item 
for each PR in GitHub (for each different Python branch a PR was created for), while 
the Weekly Developer In Residence report may consolidate these into a single item.

---

## Installation and usage

### Installation

_GitHub Result Summary_ can be installed by:<br>
1- running `git clone https://github. com/surfaceowl/python_weekly_dir_detail.git`.<br>
2- Set up a GitHub Access Token under your GitHub account.  See https://docs.github.
com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access
-token for details <br>
3. Navigate to the root directory of the project.<br>
4. Create a virtual environment using python 3.10 <br>
5. Under the root directory run `python -m pip install -r requirements.txt`.  <br>
6. Finally, edit the `config.py` file to point to the GitHub repo you want to scan. <br>
7. run main

It requires Python 3.10 to run, uses the useful [PyGitHub](https://pypi.
org/project/PyGithub/) library to manage the GitHub API.  Otherwise, the project has 
minimal dependencies.  

### Usage

Modify `config.py` as needed, and run main.  When running against large repos (e.g., 
cpython) some queries can take a long time (e.g, 5 min) due to limitations in 
the GitHub API and the PyGitHub library.  As an example, GitHub returns the results 
from the Pull Request API in chunks, but does not provide a utility to limit search 
results by filtering on Pull Requests updates since, or between certain dates.

The module is fast for very recent searches (e.g., within a few weeks), but as 
searched date ranges go further back in time they take much longer due since the GitHub 
API does not provide server-side filtering by key dates (e.g., pr update dates, or 
closed dates).

Importantly, please note that the authenticated GitHub token has an 
hourly limit of 5,000 requests before it resets (every hour).  Un-authenticated 
GitHub API requests are limited to 60 per hour, so not useful for projects like this.

When you eventually exceed your hourly usage rate, the easiest solution is to wait 
until your API usage is reset.  Use the `check_github_usage_limit.py` script to 
quickly see your current usage, your hourly API limit and the timestamp when your 
usage count is reset by GitHub.

### NOTE: This is an omega project with the bare minimum development and testing.  
#### Suggested improvements and feature requests are welcome via GitHub.

## Used by

You could be the first!


## Authors

Chris Brousseau; chris@surfaceowl.com
