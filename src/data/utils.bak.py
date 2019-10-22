import pytz
import datetime
import logging
import pathlib
import sys


def configure_logging(log_path: pathlib.Path, log_name: str) -> None:
    """ Configure logger

    Args:
        log_path: The output directory for the log file
        log_name: The logger name
    """
    datetime_string = datetime.datetime.now().strftime('.%Y-%m-%d--%H-%M-%S')
    log_filename = log_name + datetime_string + '.log'
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    fh = logging.FileHandler(filename=log_path / log_filename,
                             encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)


# def naive_dt_to_sydney(naive_dt: datetime) -> datetime:
#     """ Converts a naive datetime object from UTC to an aware
#         datetime object in Sydney timezone
#
#     Args:
#         naive_dt: The naive datetime object in UTC
#
#     Returns:
#         The aware datetime object in Sydney timezone
#     """
#     target_tz = pytz.timezone('Australia/Sydney')
#     aware_utc_dt = pytz.utc.localize(naive_dt)
#     aware_sydney_dt = aware_utc_dt.astimezone(target_tz)
#     return aware_sydney_dt
#
#
# def timestamp_to_sydney(timestamp: int) -> datetime:
#     """ Convert UTC timestamp to aware datetime object in Sydney timezone
#
#     Args:
#         timestamp: The UTC timestamp to be converted
#
#     Returns:
#         The aware datetime object in Sydney timezone
#     """
#     naive_dt = datetime.datetime.utcfromtimestamp(timestamp)
#     return naive_dt_to_sydney(naive_dt)
