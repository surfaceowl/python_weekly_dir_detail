"""
test GitHub queries for specific issue results we know were reported on various
weekly Developer In Residence Reports
15 Nov - 21 Nov 2021: https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
"""
import datetime

from config import developer_ids
from config import end_date_buffer
from utilities import check_github_rate_limit
from weekly_issues_summary import filter_issues
from weekly_issues_summary import get_issues


def test_get_issues_from_15to21nov():
    """
    The dev blog cites 14 issues total - 13 closed, 1 opened, but this does not
    account for shadow issues across different python branches (e.g. 3.10, 3.9, etc.)
    manual count of issues using issue summaries from blog is 39
    e.g., 45831 on Roundup translates to three issues on GitHub:  25596, 25597, 25598
    15-21 Nov - dev blog report at:
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    :return:
    """
    check_github_rate_limit()
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 15, 00, 00, 00)
    end_date = datetime.datetime(2021, 11, 21, 23, 59, 59)

    issues_all = get_issues(start_date)

    assert (
        len(
            filter_issues(
                issues_all, developer_ids, start_date, end_date, end_date_buffer
            )
        )
        == 37
    )
