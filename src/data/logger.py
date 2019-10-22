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
