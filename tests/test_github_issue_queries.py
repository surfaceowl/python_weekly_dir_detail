"""
test github queries for specific issue results we know were reported on various
weekly Developer In Residence Reports
15 Nov - 21 Nov 2021: https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/

"""

import datetime

from weekly_issues_summary import filter_issues
from config import issues_all


def test_get_issues_from_15to21nov():
    """
    15-21 Nov - dev blog report at:
    https://lukasz.langa.pl/4f7c2091-2a74-48ab-99d7-8521c4fa8363/
    """
    # set dates for this test
    start_date = datetime.datetime(2021, 11, 15, 00, 00, 00)
    end_date = datetime.datetime(2021, 11, 21, 23, 59, 59)

    assert len(filter_issues(issues_all)) == 34
