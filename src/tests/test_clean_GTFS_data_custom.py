import unittest
import gtfstk
from pathlib import Path

import BusGAN.project.custom_cleaners as custom_clean


class TestCleanGTFSDataCustom(unittest.TestCase):
    def setUp(self):
        self.in_dir_path = Path('../../data/gtfs/filtered_bus_feeds')

        def test_clean_method(gtfs_name, problem_msg, check_f, clean_f):
            """
                The main method used for testing

            Args:
                gtfs_name (str): The name of the file with the problem
                problem_msg (str): The problem message as reported by gtfstk.validate()
                check_f (function): The function from gtfstk which checks if the problem exists
                clean_f (function): The custom made function that cleans the problem

            Returns:
                f: the clean feed
            """
            f = gtfstk.feed.read_gtfs(self.in_dir_path / gtfs_name, dist_units='m')
            # Check that the error tested exists before the cleaning process
            prior_problems = check_f(f, as_df=True, include_warnings=True)
            self.assertTrue(problem_msg in prior_problems['message'].values)
            f = clean_f(f)
            # Check if cleaning process removed the problem
            post_problems = check_f(f, as_df=True, include_warnings=True)
            self.assertFalse(problem_msg in post_problems['message'].values)
            return f

        self.test_clean_method = test_clean_method

    def test_clean_repeated_service_id(self):
        gtfs_name = 'Champaign, IL, USA - champaign-urbana-mass-transit-district-162.zip'
        problem_msg = 'Repeated service_id'
        check_f = gtfstk.check_calendar
        clean_f = custom_clean.clean_repeated_service_id
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_route_text_color(self):
        gtfs_name = 'Paris, France - stif-822.zip'
        problem_msg = 'Invalid route_text_color; maybe has extra space characters'
        check_f = gtfstk.check_routes
        clean_f = custom_clean.clean_route_text_color
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_repeated_pair_trip_id_stop_sequence(self):
        gtfs_name = 'Taichung City, Taiwan - taiwan-955.zip'
        problem_msg = 'Repeated pair (trip_id, stop_sequence)'
        check_f = gtfstk.check_stop_times
        clean_f = custom_clean.clean_repeated_pair_trip_id_stop_sequence
        f = self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)
        # Test if the average works correctly
        # The trip_id, stop_sequence combination below has arrival/departure time
        # 16:15:11 and 16:15:01 in the initial feed. So we expect 16:15:06
        trip_id = 'TC_WD_20190101_20191231_TC_1_304_0_16:15'
        stop_sequence = 1
        average_times = f.stop_times.loc[(f.stop_times['trip_id']==trip_id)
                                                & (f.stop_times['stop_sequence']==stop_sequence),
                                         ['arrival_time','departure_time']]
        self.assertEqual(average_times.iloc[0, 0], '16:15:06')
        self.assertEqual(average_times.iloc[0, 1], '16:15:06')

    def test_clean_repeated_pair_service_id_date(self):
        gtfs_name = 'Champaign, IL, USA - champaign-urbana-mass-transit-district-162.zip'
        problem_msg = 'Repeated pair (service_id, date)'
        check_f = gtfstk.check_calendar_dates
        clean_f = custom_clean.clean_repeated_pair_service_id_date
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_feed_lang_Rzeszow(self):
        gtfs_name = 'Rzeszow, Poland - ztm-rzeszow-1009.zip'
        problem_msg = 'Invalid feed_lang; maybe has extra space characters'
        check_f = gtfstk.check_feed_info
        clean_f = custom_clean.clean_invalid_feed_lang_Rzeszow
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_agency_name_amtrak(self):
        gtfs_name = 'United States - amtrak-1136.zip'
        problem_msg = 'Invalid agency_name; maybe has extra space characters'
        check_f = gtfstk.check_agency
        clean_f = custom_clean.clean_invalid_agency_name_amtrak
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_agency_lang_Cagliari(self):
        gtfs_name = 'Cagliari, Province of Cagliari, Italy - ctm-cagliari-1098.zip'
        problem_msg = 'Invalid agency_lang; maybe has extra space characters'
        check_f = gtfstk.check_agency
        clean_f = custom_clean.clean_invalid_agency_lang_Cagliari
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_agency_lang_Fairbanks(self):
        gtfs_name = 'Fairbanks, AK, USA - macs-transit-634.zip'
        problem_msg = 'Invalid agency_lang; maybe has extra space characters'
        check_f = gtfstk.check_agency
        clean_f = custom_clean.clean_invalid_agency_lang_Fairbanks
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_agency_id_column_present_in_routes_but_not_in_agency(self):
        gtfs_name = 'Vancouver, BC, Canada - c-tran-vancouver-1013.zip'
        problem_msg = 'agency_id column present in routes but not in agency'
        check_f = gtfstk.check_routes
        clean_f = custom_clean.clean_agency_id_column_present_in_routes_but_not_in_agency
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_undefined_service_id(self):
        gtfs_name = 'Montreal, QC, Canada - agence-metropolitaine-de-transport-135.zip'
        problem_msg = 'Undefined service_id'
        check_f = gtfstk.check_trips
        clean_f = custom_clean.clean_undefined_service_id
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_agency_url_Luxembourg(self):
        gtfs_name = 'Luxembourg - verkeiersverbond-1034.zip'
        problem_msg = 'Invalid agency_url; maybe has extra space characters'
        check_f = gtfstk.check_agency
        clean_f = custom_clean.clean_invalid_agency_url_Luxembourg
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_agency_url_Nice(self):
        gtfs_name = 'Nice, France - lignes-dazur-738.zip'
        problem_msg = 'Invalid agency_url; maybe has extra space characters'
        check_f = gtfstk.check_agency
        clean_f = custom_clean.clean_invalid_agency_url_Nice
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_departure_time(self):
        gtfs_name = 'Chiang Mai, Mueang Chiang Mai District, Chiang Mai, Thailand - greenbus-thailand-784.zip'
        problem_msg = 'Invalid departure_time; maybe has extra space characters'
        check_f = gtfstk.check_stop_times
        clean_f = custom_clean.clean_invalid_departure_time
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_arrival_time(self):
        gtfs_name = 'Chiang Mai, Mueang Chiang Mai District, Chiang Mai, Thailand - greenbus-thailand-784.zip'
        problem_msg = 'Invalid arrival_time; maybe has extra space characters'
        check_f = gtfstk.check_stop_times
        clean_f = custom_clean.clean_invalid_arrival_time
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_undefined_shape_id(self):
        gtfs_name = 'Buenos Aires, Autonomous City of Buenos Aires, Argentina - colectivos-buenos-aires-1037.zip'
        problem_msg = 'Undefined shape_id'
        check_f = gtfstk.check_trips
        clean_f = custom_clean.clean_undefined_shape_id
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_undefined_stop_id(self):
        gtfs_name = 'Izmit, İzmit,Kocaeli, Turkey - kocaeli-buyuksehir-belediyesi-964.zip'
        problem_msg = 'Undefined stop_id'
        check_f = gtfstk.check_stop_times
        clean_f = custom_clean.clean_undefined_stop_id
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_route_url(self):
        gtfs_name = 'Asheville, NC, USA - asheville-transit-service-152.zip'
        problem_msg = 'Invalid route_url; maybe has extra space characters'
        check_f = gtfstk.check_routes
        clean_f = custom_clean.clean_invalid_route_url
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_invalid_stop_url(self):
        gtfs_name = 'Kuopio, Finland - city-of-kuopio-731.zip'
        problem_msg = 'Invalid stop_url; maybe has extra space characters'
        check_f = gtfstk.check_stops
        clean_f = custom_clean.clean_invalid_stop_url
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_trip_has_no_stop_times(self):
        gtfs_name = 'Athens, Greece - athens-urban-transport-organisation-580.zip'
        problem_msg = 'Trip has no stop times'
        check_f = gtfstk.check_trips
        clean_f = custom_clean.clean_trip_has_no_stop_times
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_first_last_timepoint_stop_time_missing(self):
        gtfs_name = 'Bishop, CA 93514, USA - eastern-sierra-transit-602.zip'
        problem_msg = 'First/last/time point arrival/departure time missing'
        check_f = gtfstk.check_stop_times
        clean_f = custom_clean.first_last_timepoint_stop_time_missing
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)

    def test_clean_shape_dist_traveled_decreases(self):
        for gtfs_name in ['Izmit, İzmit,Kocaeli, Turkey - kocaeli-buyuksehir-belediyesi-964.zip',
                          'Nancy, France - communaute-urbaine-du-grand-nancy-596.zip',
                          'Nancy, France - grand-nancy-1068.zip',
                          'Nice, France - lignes-dazur-738.zip']:
            with self.subTest(gtfs_name=gtfs_name):
                problem_msg = 'shape_dist_traveled decreases on a trip'
                f = gtfstk.feed.read_gtfs(self.in_dir_path / gtfs_name, dist_units='m')
                # Check that the error tested exists before the cleaning process
                # Problems in this category can come from two different tables
                prior_problems = gtfstk.check_stop_times(f, as_df=True, include_warnings=True)
                if f.shapes is not None:
                    prior_problems = prior_problems.append(gtfstk.check_shapes(f, as_df=True, include_warnings=True), ignore_index=True)
                self.assertTrue(problem_msg in prior_problems['message'].values)
                f = custom_clean.clean_shape_dist_traveled_decreases(f)
                # Check if cleaning process removed the problem
                post_problems = gtfstk.check_stop_times(f, as_df=True, include_warnings=True)
                if f.shapes is not None:
                    post_problems = post_problems.append(gtfstk.check_shapes(f, as_df=True, include_warnings=True), ignore_index=True)
                self.assertFalse(problem_msg in post_problems['message'].values)

    def test_clean_parent_station_must_be_well_defined(self):
        gtfs_name = 'Anaheim, CA, USA - anaheim-resort-transportation-410.zip'
        problem_msg = 'A parent station must be well-defined'
        check_f = gtfstk.check_stops
        clean_f = custom_clean.clean_parent_station_must_be_well_defined
        self.test_clean_method(gtfs_name, problem_msg, check_f, clean_f)


if __name__ == '__main__':
    unittest.main()
