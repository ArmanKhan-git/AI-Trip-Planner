import re

_ISO_DURATION = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?)?$"
)


def format_duration(duration: str) -> str:
    """
    Converts an ISO8601 duration to a readable string:
      PT8H27M   -> 8 hr 27 min
      P1DT6H15M -> 30 hr 15 min
    Strings that are not ISO durations are returned unchanged.
    """

    if not duration:
        return "Unknown"

    match = _ISO_DURATION.match(duration.strip())

    if not match or not any(match.groupdict().values()):
        return duration

    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0) + days * 24
    minutes = int(match.group("minutes") or 0)

    parts = []

    if hours:
        parts.append(f"{hours} hr")

    if minutes:
        parts.append(f"{minutes} min")

    return " ".join(parts) or "0 min"
