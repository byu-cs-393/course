"""Calendar helpers shared by build.py and canvas_sync.py.

Derived from each schedule row's `dates` ("Oct 19–24", "Sep 28–Oct 3") and the
course's meeting days (Tuesday & Thursday), so nothing date-like is hand-typed twice.
"""
import re
from datetime import date

YEAR = 2026
MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS = {m: i for i, m in enumerate(MON[1:], 1)}
MEET_DAYS = (1, 3)   # Tuesday, Thursday (date.weekday())
DAY_NAME = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def start_date(dates):
    """First calendar day of a schedule 'dates' range, as (month, day)."""
    m = re.match(r"([A-Z][a-z]{2})\s+(\d+)", dates)
    return MONTHS[m.group(1)], int(m.group(2))


def end_date(dates):
    """Last calendar day of a schedule 'dates' range, as (month, day)."""
    tail = dates.split("–")[-1].strip()
    m = re.match(r"([A-Z][a-z]{2})?\s*(\d+)", tail)
    mon = m.group(1) or dates.split()[0]
    return MONTHS[mon], int(m.group(2))


def class_days(dates):
    """The Tue/Thu class meetings inside a week's date range, in order."""
    start, end = date(YEAR, *start_date(dates)), date(YEAR, *end_date(dates))
    return [date.fromordinal(o) for o in range(start.toordinal(), end.toordinal() + 1)
            if date.fromordinal(o).weekday() in MEET_DAYS]


def day_label(d):
    """'Tuesday, Oct 20'"""
    return f"{DAY_NAME[d.weekday()]}, {MON[d.month]} {d.day}"


def week_label(week, dates):
    """'Week 08 (Oct 19–24)'"""
    return f"Week {week:02d} ({dates})"
