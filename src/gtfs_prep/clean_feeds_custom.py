# 2nd round of cleaning the GTFS data
# now we are solving the problems in
# filtered.gtfs.problems.csv.

from pathlib import Path
import os
import pandas as pd
import gtfstk
import shutil
import logging
from BusGAN.project.utils import configure_logging
from BusGAN.project.custom_cleaners import *

PROBLEMS_FILE = 'filtered_empty_feeds_invalid_columns.gtfs.problems.csv'
INPUT_GTFS_FOLDER_NAME = 'filtered_empty_feeds_invalid_columns'
OUTPUT_GTFS_FOLDER_NAME = 'cleaned_feeds_custom'

# Read the problems in a df
problems_dir_path = Path('../../output/gtfs problems')
problems_file_path = problems_dir_path / PROBLEMS_FILE
problems_df = pd.read_csv(problems_file_path)
# Filter the problems we care about
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
    'Repeated pair (trip_id, stop_sequence)',
    'agency_id column present in routes but not in agency'
]
problems_df = problems_df[problems_df['message'].isin(problems_list)]
gtfs_names_with_problems = problems_df['gtfs_name'].unique()

data_dir_path = Path('../../data/gtfs')
in_dir_path = data_dir_path / INPUT_GTFS_FOLDER_NAME

out_dir_path = data_dir_path / OUTPUT_GTFS_FOLDER_NAME
out_dir_path.mkdir(parents=True, exist_ok=True)

log_name = os.path.basename(__file__).rsplit('.', 1)[0]
configure_logging(log_path=data_dir_path, log_name=log_name)
logger = logging.getLogger(log_name)

total_gtfs_files = sum(1 for _ in in_dir_path.glob('*.zip'))
cur_counter = 0

for gtfs_file_path in in_dir_path.glob('*.zip'):
    cur_counter = cur_counter + 1
    gtfs_name = gtfs_file_path.name
    if gtfs_name in gtfs_names_with_problems:
        logger.info(f'Cleaning {gtfs_name} ({cur_counter}/{total_gtfs_files})')
        try:
            cur_problems = problems_df[problems_df['gtfs_name'] == gtfs_name]
            problem_msgs = cur_problems['message'].values
            feed = gtfstk.feed.read_gtfs(gtfs_file_path, dist_units='m')
            if ('First/last/time point arrival/departure time missing'
                    in problem_msgs):
                feed = first_last_timepoint_stop_time_missing(feed)
            if ('Invalid stop_url; maybe has extra space characters'
                    in problem_msgs):
                feed = invalid_stop_url(feed)
            if ('Invalid route_url; maybe has extra space characters'
                    in problem_msgs):
                feed = invalid_route_url(feed)
            if 'shape_dist_traveled decreases on a trip' in problem_msgs:
                feed = shape_dist_traveled_decreases(feed)
            if ('Invalid agency_lang; maybe has extra space characters'
                    in problem_msgs):
                if 'Cagliari' in gtfs_name:
                    feed = invalid_agency_lang_Cagliari(feed)
                if 'Fairbanks' in gtfs_name:
                    feed = invalid_agency_lang_Fairbanks(feed)
            if ('Invalid agency_url; maybe has extra space characters'
                    in problem_msgs):
                if 'Luxembourg' in gtfs_name:
                    feed = invalid_agency_url_Luxembourg(feed)
                if 'Nice' in gtfs_name:
                    feed = invalid_agency_url_Nice(feed)
            if ('Invalid agency_name; maybe has extra space characters'
                    in problem_msgs):
                if 'United States - amtrak-1136.zip' == gtfs_name:
                    feed = invalid_agency_name_amtrak(feed)
            if ('Invalid feed_lang; maybe has extra space characters'
                    in problem_msgs):
                if 'Rzeszow' in gtfs_name:
                    feed = invalid_feed_lang_Rzeszow(feed)
            if ('Invalid route_text_color; maybe has extra space characters'
                    in problem_msgs):
                feed = route_text_color(feed)
            if 'Repeated pair (trip_id, stop_sequence)' in problem_msgs:
                feed = repeated_pair_trip_id_stop_sequence(feed)
            if ('Invalid stop_id; maybe has extra space characters'
                    in problem_msgs):
                if 'Marin' in gtfs_name:
                    feed = invalid_stop_id_Marin(feed)
            if ('agency_id column present in routes but not in agency'
                    in problem_msgs):
                if 'Vancouver' in gtfs_name:
                    feed = agency_id_column_in_routes_not_in_agency_Vanc(feed)

            # if 'A parent station must be well-defined' in problem_msgs:
            #     feed = clean_parent_station_must_be_well_defined(feed)
            # if 'Undefined shape_id' in problem_msgs:
            #     feed = clean_undefined_shape_id(feed)
            # if 'Repeated service_id' in problem_msgs:
            #     feed = clean_repeated_service_id(feed)
            # if 'Repeated pair (service_id, date)' in problem_msgs:
            #     feed = clean_repeated_pair_service_id_date(feed)
            # if 'Undefined stop_id' in problem_msgs:
            #     feed = clean_undefined_stop_id(feed)
            # if 'Invalid arrival_time; maybe has extra space characters' in problem_msgs:
            #     feed = clean_invalid_arrival_time(feed)
            # if 'Invalid departure_time; maybe has extra space characters' in problem_msgs:
            #     feed = clean_invalid_departure_time(feed)
            # if 'Undefined service_id' in problem_msgs:
            #     feed = clean_undefined_service_id(feed)
            # if 'agency_id column present in routes but not in agency' in problem_msgs:
            #     feed = clean_agency_id_column_present_in_routes_but_not_in_agency(feed)
            # if 'Trip has no stop times' in problem_msgs:
            #     feed = clean_trip_has_no_stop_times(feed)
            gtfstk.feed.write_gtfs(feed, out_dir_path / gtfs_name)
            logger.info(f'Completed')
        except Exception as e:
            logger.exception(f'Exception while cleaning {gtfs_name}: {e}')
    else:
        logger.info(f'Copying {gtfs_name} ({cur_counter}/{total_gtfs_files})')
        try:
            shutil.copy(str(gtfs_file_path), str(out_dir_path))
            logger.info(f'Completed')
        except Exception as e:
            logger.exception(f'Exception while copying {gtfs_name}: {e}')
