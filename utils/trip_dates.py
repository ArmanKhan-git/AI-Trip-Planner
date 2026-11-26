from datetime import date, datetime
from typing import Optional, Tuple, Union

DateLike = Union[str, date, None]


def _to_date(value: DateLike) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def nights_and_days(departure: DateLike, returning: DateLike) -> Optional[Tuple[int, int]]:
    """
    Departing Nov 28 and returning Dec 5 is 7 nights and 8 calendar days
    (both the arrival day and the departure day are part of the trip).
    """

    dep = _to_date(departure)
    ret = _to_date(returning)

    if not dep or not ret or ret <= dep:
        return None

    nights = (ret - dep).days
    return nights, nights + 1
