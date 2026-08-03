import re


def format_duration(duration: str) -> str:
    """
    Converts ISO8601 duration (PT8H27M) to:
    8 hr 27 min
    """

    if not duration:
        return "Unknown"

    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration)

    if not match:
        return duration

    hours = match.group(1)
    minutes = match.group(2)

    parts = []

    if hours:
        parts.append(f"{int(hours)} hr")

    if minutes:
        parts.append(f"{int(minutes)} min")

    return " ".join(parts)