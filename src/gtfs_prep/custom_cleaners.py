import gtfstk
import pandas as pd
import numpy as np


# def clean_repeated_service_id(feed):
#     # Drop the second occurrence
#     feed.calendar = feed.calendar.drop_duplicates(subset='service_id')
#     return feed
#
#
def route_text_color(feed):
    # Set invalid rows' color to black
    problems = gtfstk.check_routes(feed, as_df=True, include_warnings=True)
    msg = 'Invalid route_text_color; maybe has extra space characters'
    problem = problems.loc[problems['message'] == msg]
    rows = problem.loc[:, 'rows'].values[0]
    feed.routes.loc[rows, 'route_text_color'] = '000000'
    feed.routes = feed.routes
    return feed
#
#
def repeated_pair_trip_id_stop_sequence(feed):
    feed.stop_times = feed.stop_times.drop_duplicates(['trip_id',
                                                       'stop_sequence'])
    return feed
    # # TODO: refactor, can't operate on the arrival_time or departure_time columns in the original feed since values can be >24
    # # Get the duplicated rows with equal pairs (trip_id, stop_sequence), get both rows
    # duplicated_rows = feed.stop_times[feed.stop_times[["trip_id", "stop_sequence"]].duplicated(keep=False)]
    # # Convert the time columns from string to datetime objects
    # duplicated_rows.loc[:, ['arrival_time', 'departure_time']] = duplicated_rows[['arrival_time', 'departure_time']].apply(pd.to_datetime, format='%H:%M:%S')
    # # Convert the time columns from datetime objects to int in order to average duplicated rows
    # duplicated_rows.loc[:, ['arrival_time', 'departure_time']] = duplicated_rows[['arrival_time', 'departure_time']].values.astype(np.int64)
    # # Average the times of the duplicated rows, the averages df has 4 columns, [trip_id, stop_sequence, arrival_time, departure_time]
    # averages = duplicated_rows.groupby(["trip_id", "stop_sequence"], as_index=False)[['arrival_time', 'departure_time']].mean()
    # # Convert from int to datetime
    # averages.loc[:, ['arrival_time', 'departure_time']] = averages[['arrival_time', 'departure_time']].apply(pd.to_datetime)
    # # Convert from datetime to string
    # averages.loc[:, ['arrival_time', 'departure_time']] = averages[['arrival_time', 'departure_time']].apply(lambda x: x.dt.strftime('%H:%M:%S'))
    # # Join the two dfs, now duplicated_rows has 'arrival_time_x', 'departure_time_x' and 'arrival_time_y', 'departure_time_y'
    # # _x are the ones it already had, _y are the averages
    # duplicated_rows = duplicated_rows.merge(averages, on=["trip_id", "stop_sequence"])
    # # Create two new columns to have same structure as before
    # duplicated_rows[['arrival_time', 'departure_time']] = duplicated_rows[['arrival_time_y', 'departure_time_y']]
    # # Drop the 4 unused columns
    # duplicated_rows = duplicated_rows.drop(columns=['arrival_time_x', 'departure_time_x', 'arrival_time_y', 'departure_time_y'])
    # # Drop the duplicated and keep only the first occurrence
    # duplicated_rows = duplicated_rows.drop_duplicates(subset=["trip_id", "stop_sequence"])
    # # From our initial stop_times df drop all duplicates
    # feed.stop_times = feed.stop_times.drop_duplicates(subset=["trip_id", "stop_sequence"], keep=False)
    # # # This is needed, mentioned in the gtfstk.Feed constructor
    # # feed.stop_times = feed.stop_times
    # # Order the columns in the df we are about to add in the same order as the stop_times df
    # duplicated_rows = duplicated_rows[list(feed.stop_times.columns.values)]
    # # Finally append the averaged df
    # feed.stop_times = feed.stop_times.append(duplicated_rows, ignore_index=True)
    # #feed.stop_times = feed.stop_times
    return feed
#
#
# def clean_repeated_pair_service_id_date(feed):
#     feed.calendar_dates = feed.calendar_dates.drop_duplicates(['service_id', 'date'])
#     return feed
#
#
def invalid_feed_lang_Rzeszow(feed):
    feed.feed_info.loc[0, ['feed_lang', 'feed_version']] = ['pl', '2019-01-16 08:07:18']
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.feed_info = feed.feed_info
    return feed
#
#
def invalid_agency_name_amtrak(feed):
    feed.agency.at[0, 'agency_name'] = 'UNK'
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.agency = feed.agency
    return feed
#
#
def invalid_agency_lang_Cagliari(feed):
    feed.agency.at[0, 'agency_lang'] = 'it'
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.agency = feed.agency
    return feed


def invalid_agency_lang_Fairbanks(feed):
    feed.agency.at[0, 'agency_lang'] = 'en'
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.agency = feed.agency
    return feed
#
#
def agency_id_column_in_routes_not_in_agency_Vanc(feed):
    feed.routes = feed.routes.drop(columns='agency_id')
    return feed
#
#
# def clean_undefined_service_id(feed):
#     problems = gtfstk.check_trips(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Undefined service_id'].loc[:, 'rows'].values[0]
#     feed.trips = feed.trips.drop(rows)
#     return feed
#
#
def invalid_agency_url_Luxembourg(feed):
    feed.agency.loc[0:4, 'agency_url'] = 'http://luxembourg.public.lu/en/se-deplacer-au-luxembourg/en-commun/index.html'
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.agency = feed.agency
    return feed


def invalid_agency_url_Nice(feed):
    feed.agency.at[0, 'agency_url'] = 'https://www.lignesdazur.com/'
    # This is needed, mentioned in the gtfstk.Feed constructor
    feed.agency = feed.agency
    return feed
#
#
# def clean_invalid_departure_time(feed):
#     problems = gtfstk.check_stop_times(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Invalid departure_time; maybe has extra space characters'].loc[:, 'rows'].values[0]
#     feed.stop_times.loc[rows, 'departure_time'] = np.nan
#     feed.stop_times = feed.stop_times
#     return feed
#
#
# def clean_invalid_arrival_time(feed):
#     problems = gtfstk.check_stop_times(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Invalid arrival_time; maybe has extra space characters'].loc[:, 'rows'].values[0]
#     feed.stop_times.loc[rows, 'arrival_time'] = np.nan
#     feed.stop_times = feed.stop_times
#     return feed
#
#
# def clean_undefined_shape_id(feed):
#     problems = gtfstk.check_trips(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Undefined shape_id'].loc[:, 'rows'].values[0]
#     feed.trips.loc[rows, 'shape_id'] = np.nan
#     feed.trips = feed.trips
#     return feed
#
#
# def clean_undefined_stop_id(feed):
#     problems = gtfstk.check_stop_times(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Undefined stop_id'].loc[:, 'rows'].values[0]
#     feed.stop_times = feed.stop_times.drop(rows)
#     return feed
#
#
def invalid_route_url(feed):
    problems = gtfstk.check_routes(feed, as_df=True, include_warnings=True)
    problem = problems.loc[problems['message'] ==
                           'Invalid route_url; maybe has ' \
                           'extra space characters']
    rows = problem.loc[:, 'rows'].values[0]
    feed.routes.loc[rows, 'route_url'] = np.nan
    feed.routes = feed.routes
    return feed
#
#
def invalid_stop_url(feed):
    problems = gtfstk.check_stops(feed, as_df=True, include_warnings=True)
    problem = problems.loc[problems['message'] ==
                           'Invalid stop_url; maybe has ' \
                           'extra space characters']
    rows = problem.loc[:, 'rows'].values[0]
    feed.stops.loc[rows, 'stop_url'] = np.nan
    feed.stops = feed.stops
    return feed


def invalid_stop_id_Marin(feed):
    problems = gtfstk.check_stops(feed, as_df=True, include_warnings=True)
    problem = problems.loc[problems['message'] ==
                           'Invalid stop_id; maybe has extra space characters']
    rows = problem.loc[:, 'rows'].values[0]
    feed.stops = feed.stops.drop(rows)
    feed.stops = feed.stops
    return feed
#
#
# def clean_trip_has_no_stop_times(feed):
#     problems = gtfstk.check_trips(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'Trip has no stop times'].loc[:, 'rows'].values[0]
#     feed.trips = feed.trips.drop(rows)
#     return feed
#
#
def first_last_timepoint_stop_time_missing(feed):
    # If timepoint then change from 1 to 0 and try again
    # if the problem persists, remove all trips with that trip_id
    problems = gtfstk.check_stop_times(feed, as_df=True, include_warnings=True)
    problem = problems.loc[problems['message'] ==
                           'First/last/time point ' \
                           'arrival/departure time missing']
    rows = problem.loc[:, 'rows'].values[0]
    if 'timepoint' in feed.stop_times.columns:
        feed.stop_times.loc[rows, 'timepoint'] = 0
        feed.stop_times = feed.stop_times
        problems = gtfstk.check_stop_times(feed, as_df=True,
                                           include_warnings=True)
    # Now problems exist only if start/end stoptime missing
    if (not problems.empty and
            'First/last/time point '
            'arrival/departure time missing' in problems['message'].values):
        problem = problems.loc[problems['message'] ==
                               'First/last/time point ' \
                               'arrival/departure time missing']
        # Get the rows with the missing first/last times
        rows = problem.loc[:, 'rows'].values[0]
        # Get the trip ids of those rows
        trip_ids = feed.stop_times.loc[rows, 'trip_id'].values
        # Get the indices of the stop times with those trip_ids
        indices = feed.stop_times[
            feed.stop_times['trip_id'].isin(trip_ids)
        ].index
        feed.stop_times = feed.stop_times.drop(indices)
    return feed
#
#
def shape_dist_traveled_decreases(feed):
    error_msg = 'shape_dist_traveled decreases on a trip'
    # The problem can come from two different tables
    if feed.shapes is not None:
        problems = gtfstk.check_shapes(feed, as_df=True, include_warnings=True)
        if not problems.empty and error_msg in problems['message'].values:
            feed.shapes = feed.shapes.drop(columns='shape_dist_traveled')
    problems = gtfstk.check_stop_times(feed, as_df=True, include_warnings=True)
    if not problems.empty and error_msg in problems['message'].values:
        feed.stop_times = feed.stop_times.drop(columns='shape_dist_traveled')
    return feed
#
#
# def clean_parent_station_must_be_well_defined(feed):
#     problems = gtfstk.check_stops(feed, as_df=True, include_warnings=True)
#     rows = problems[problems['message'] == 'A parent station must be well-defined'].loc[:, 'rows'].values[0]
#     feed.stops.loc[rows, 'parent_station'] = np.nan
#     feed.stops = feed.stops
#     return feed
