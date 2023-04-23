import csv
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
    with open(DATELIST_P, "r", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        schedule = [
            (datetime.fromisoformat(row[0]), row[1])
            for row in reader
        ]
    i = bisect_right(
        schedule, datetime.now(), key=lambda x: x[0]
    )
    return schedule[i], schedule[i+1]
