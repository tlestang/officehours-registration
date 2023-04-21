from datetime import datetime
from bisect import bisect_right


DATELIST_P = "dates.txt"


def find_gt(a, x):
    "Find leftmost value greater than x"
    i = bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError


def find_next_two_dates():
    with open(DATELIST_P, "r") as f:
        dates = [datetime.fromisoformat(d.strip()) for d in f]
        next_session = find_gt(dates, datetime.now())
        next_next_session = find_gt(dates, next_session)

        return next_session, next_next_session
