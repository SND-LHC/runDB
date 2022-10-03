"""Helper functions for the mongodbadapter."""

import datetime


def validate_str(input_string):
    """Validate whether input_string is of string type.

    If it is not of String type it returns False.

    :param input_string: value that needs to be tested.
    """
    if isinstance(input_string, str):
        return True
    return False


def validate_datetime(input_datetime):
    """Validate whether input_datetime is of datetime type.

    If it is not of datetime type it returns False.

    :param input_datetime: value that needs to be tested.
    """
    if isinstance(input_datetime, datetime.datetime):
        return True
    return False


def sanitize_str(input_string):
    """Remove spaces at the beginning and at the end of the string and returns the String without spaces.

    :param input_string: string that will be sanitized.
    """
    return input_string.strip()


def convert_date(input_date_string):
    """Convert a date string to a datetime Object.

    :param 	input_date_string: String representing a date
            Accepted String formats: "Year", "Year-Month", "Year-Month-Day", "Year-Month-Day Hours",
            "Year-Month-Day Hours-Minutes", "Year-Month-Day Hours-Minutes-Seconds".
    :throw 	ValueError: If input_date_string is not as specified.
    """
    # Accepted formats for input_date_string
    time_stamp_str_format = [
        "%Y",
        "%Y-%m",
        "%Y-%m-%d",
        "%Y-%m-%d %H",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]
    datetime_value = None

    for time_stamp_format in time_stamp_str_format:
        try:
            datetime_value = datetime.datetime.strptime(  # pylint: disable=no-member
                input_date_string, time_stamp_format
            )
            break
        except ValueError:
            pass

    if datetime_value is None:
        raise ValueError(
            "Please pass the correct date input. This date string should "
            "contain only digits/:/ /-. The minimum length could be 4 digits, "
            "representing the year. "
        )
    return datetime_value


def create_uri(connection_dict):
    """Create URI for mongo using connection dict."""
    user = connection_dict["user"]
    password = connection_dict["password"]
    db = connection_dict["db_name"]
    host = connection_dict["host"]
    port = connection_dict["port"]
    return f"mongodb://{user}:{password}@{host}:{port}/{db}"
