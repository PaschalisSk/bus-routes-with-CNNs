# Goes through the zips in a folder and outputs problems in a csv

from pathlib import Path
import gtfstk
import pandas as pd
import datetime
import logging
import sys

def configure_logging(log_path: Path, log_name: str) -> None:
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

GTFS_FOLDER = 'removed_optional_tables'
# previous output file to filter the gtfs files we are searching for problems
# i.e. search only files that had problems
PROBLEMS_FILE = None#'filtered_empty_feeds_invalid_columns.gtfs.problems.csv'

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / GTFS_FOLDER

out_dir_path = Path('../../output/gtfs problems')
out_dir_path.mkdir(parents=True, exist_ok=True)
out_file_name = GTFS_FOLDER + '.gtfs.problems.full.csv'
out_file_path = out_dir_path / out_file_name

if PROBLEMS_FILE is not None:
    problems_dir_path = Path('../../output/gtfs problems')
    problems_file_path = problems_dir_path / PROBLEMS_FILE
    problems_df = pd.read_csv(problems_file_path)
    # Filter out the problems we don't care about (or the ones we care about)
    # problems_df = problems_df[(problems_df['message'] !=
    #                        'Repeated pair (trip_id, departure_time)')
    #                       & (problems_df['message'] != 'Feed expired')
    #                       & (problems_df['message'] !=
    #                          'Repeated pair (route_short_name, '
    #                          'route_long_name)')]
    problems_list = [
        'First/last/time point arrival/departure time missing',
        'Invalid stop_url; maybe has extra space characters',
        'Invalid route_url; maybe has extra space characters',
        'shape_dist_traveled decreases on a trip',
        'Invalid agency_lang; maybe has extra space characters',
        'Invalid agency_url; maybe has extra space characters',
        'Invalid agency_name; maybe has extra space characters',
        'Invalid feed_lang; maybe has extra space characters',
        'Invalid route_text_color; maybe has extra space characters',
        'Invalid stop_id; maybe has extra space characters',
        'Repeated pair (trip_id, stop_sequence)'
    ]
    problems_df = problems_df[problems_df['message'].isin(problems_list)]
    # Get the names of the files with problems
    # so that we can don't waste time searching the rest
    gtfs_names_with_problems = problems_df['gtfs_name'].unique()
    # Check if file exists because we may have deleted it depending on
    # the problem
    available_paths = [filepath for filepath in in_dir_path.glob('*.zip')]
    problems_paths = [in_dir_path / name for name in gtfs_names_with_problems]
    gtfs_paths = [x for x in problems_paths if x in available_paths]
else:
    gtfs_paths = [filepath for filepath in in_dir_path.glob('*.zip')]

total_gtfs_files = len(gtfs_paths)
cur_counter = 0

log_name = out_file_name.rsplit('.', 1)[0]
configure_logging(log_path=out_dir_path, log_name=log_name)
logger = logging.getLogger(log_name)

# Variable to hold all errors
dataset_problems = None
file_created = False

for gtfs_file_path in gtfs_paths:
    gtfs_name = gtfs_file_path.name
    try:
        cur_counter = cur_counter + 1
        logger.info(f'Checking {gtfs_name} ({cur_counter}/{total_gtfs_files})')
        # Dist units doesn't matter as long as we use the same at the write
        # operation
        feed = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
        feed_problems = feed.validate()
        if not feed_problems.empty:
            feed_problems.insert(0, 'gtfs_name', gtfs_name)
            if dataset_problems is None:
                dataset_problems = feed_problems
            else:
                dataset_problems = dataset_problems.append(feed_problems,
                                                           ignore_index=True)
        # Flush problems to disc
        if (dataset_problems is not None and
                (dataset_problems.shape[0] > 50 or
                 cur_counter == total_gtfs_files)):
            if not file_created:
                dataset_problems.to_csv(out_file_path, index=False)
                file_created = True
            else:
                dataset_problems.to_csv(out_file_path, mode='a',
                                        index=False, header=False)
            dataset_problems = None
    except Exception as e:
        logger.exception(f'Exception while checking {gtfs_name} {e}')


