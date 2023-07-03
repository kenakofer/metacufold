import dateutil.parser
import re
from datetime import datetime
def title_to_resolution_datetime(title):
    # Use a variety of regexes for common year and day formats to guess the closing time

    month_regex = r"(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)"
    year_regex = r"(\d{4})"
    # Day regex, which discards st or nd or th suffixes
    day_regex = r"(\d{1,2})(?:st|nd|rd|th)?"
    space_regex = r",?\.?\s+" # With . or , as puctuation

    before = {
        "regex": r"(?:before|by|on|prior to)\s+",
        "date_default": datetime(datetime.now().year, 1, 1)
    }
    during = {
        "regex": r"(?:during|in)\s+",
        "date_default": datetime(datetime.now().year, 12, 31)
    }

    full_date_regexes = [
        # Month year first
        month_regex + space_regex + year_regex,
        month_regex + space_regex + day_regex + space_regex + year_regex,
        month_regex + space_regex + day_regex,
        year_regex,
        month_regex,
    ]
    # first day of the current year
    default_datetime = datetime(datetime.now().year, 1, 1)

    for prefix in [before, during]:
        for date_regex in full_date_regexes:
            match = re.search(prefix["regex"] + date_regex, title, re.IGNORECASE)
            if match and match.groups():
                # Print out all match groups for debugging:
                print(match.groups())

                # use dateutil parser on the date portion of the match
                date = dateutil.parser.parse(" ".join(match.groups()), default=prefix["date_default"])

                # If date is in the past (before now), move it forward 1 year
                if date < datetime.now():
                    date = date.replace(year=date.year + 1)

                return date



    print("No date found in title: " + title)
    return None