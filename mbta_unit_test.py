import unittest
from mbta import MbtaErrorCodes, print_all_lines, print_stops, main
import yaml

class MbtaUnitTest(unittest.TestCase):
    def setUp(self):
        """
        Read the yaml that holds the api url
        :return:
        """
        with open(r'mbta.yaml') as file:
            self.api_dict = yaml.load(file, Loader=yaml.FullLoader)

    def test_get_lines(self):
        """
        Directly call the get_lines function
        :return:
        """
        rc = print_all_lines(self.api_dict['get_lines'])
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_get_lines_bad_url(self):
        """
        Corrupt the get_lines url to force a non-200 response
        :return:
        """
        rc = print_all_lines(self.api_dict['get_lines']+'foo')
        self.assertEqual(MbtaErrorCodes.Non200Resp, rc)

    def test_get_stops_red(self):
        """
        Get all stops for all the known lines - would need to update this if new lines added
        :return:
        """
        known_lines =  ['Blue', 'Green-B', 'Green-C', 'Green-D', 'Mattapan', 'Orange', 'Red']
        for line in known_lines:
            rc = print_stops(self.api_dict['get_stops'], line)
            self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_get_lines_bad_url(self):
        """
        Corrupt the url for the get_stops.
        :return:
        """
        rc = print_stops(self.api_dict['get_stops']+'foo', 'Red')
        self.assertEqual(MbtaErrorCodes.Non200Resp, rc)

    def test_get_lines_bad_line(self):
        """
        Verify that while the API call for a non-existent line gives a 200 response but no data
        :return:
        """
        rc = print_stops(self.api_dict['get_stops'], 'red')  # Ids are case-sensitive
        self.assertEqual(MbtaErrorCodes.NoOutput, rc)

    def test_main_get_all_lines(self):
        """
        Simulate a command-line call to main for --get-lines
        :return:
        """
        args = ['', '--get-lines']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_main_get_all_lines_extra_param(self):
        """
        Simulate a command-line call to main for --get-lines with an extra parameter
        :return:
        """
        args = ['', '--get-lines', 'Red']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_get_stops(self):
        """
        Simulate a command-line call to main for --get-stops with Green-B
        :return:
        """
        args = ['', '--get-stops', 'Green-B']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_main_get_stops_missing_param(self):
        """
        Simulate a command-line call to main for --get-stops without the needed line parameter
        :return:
        """
        args = ['', '--get-stops']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_get_stops_extra_param(self):
        """
        Simulate a command-line call to main for --get-stops with multiple lines - not supported at
        present though it is a potential enhancement - in such a case we'd need to modify this
        test to expect success.
        :return:
        """
        args = ['', '--get-stops', 'Green-B', 'Green-C']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_no_args(self):
        """
        Simulate a command-line call to main with no parameters - note we still have a single element in the
        args as we are mocking the way that argv is passed to the program.
        :return:
        """
        args = ['']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.NoArgs, rc)

    def test_main_bad_args(self):
        """
        Simulate a command-line call to main with a typo in the parameters.
        :return:
        """
        args = ['', '--get-stoops']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_help(self):
        """
        Simulate a command-line call to main with the --help parameter
        :return:
        """
        args = ['', '--help']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

if __name__ == '__main__':
    unittest.main()
