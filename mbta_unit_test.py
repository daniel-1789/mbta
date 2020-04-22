import unittest
from mbta import MbtaErrorCodes, print_all_lines, print_stops, main
import yaml

class MbtaUnitTest(unittest.TestCase):
    def setUp(self):
        with open(r'mbta.yaml') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.api_dict = yaml.load(file, Loader=yaml.FullLoader)

    def test_get_routes(self):
        rc = print_all_lines(self.api_dict['get_routes'])
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_get_routes_bad_url(self):
        rc = print_all_lines(self.api_dict['get_routes']+'foo')
        self.assertEqual(MbtaErrorCodes.Non200Resp, rc)

    def test_get_stops(self):
        rc = print_stops(self.api_dict['get_stops'], 'Red')
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_get_routes_bad_url(self):
        rc = print_stops(self.api_dict['get_stops']+'foo', 'Red')
        self.assertEqual(MbtaErrorCodes.Non200Resp, rc)

    def test_get_routes_bad_line(self):
        rc = print_stops(self.api_dict['get_stops'], 'red')
        self.assertEqual(MbtaErrorCodes.NoOutput, rc)

    def test_main_get_all_routes(self):
        args = ['', '--get-routes']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_main_get_all_routes_extra_param(self):
        args = ['', '--get-routes', 'Red']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_get_stops(self):
        args = ['', '--get-stops', 'Green-B']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

    def test_main_get_stops_missing_param(self):
        args = ['', '--get-stops']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_get_stops_extra_param(self):
        args = ['', '--get-stops', 'Green-B', 'Green-C']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_no_args(self):
        args = ['']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.NoArgs, rc)

    def test_main_bad_args(self):
        args = ['', '--get-stoops']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.BadArgs, rc)

    def test_main_help(self):
        args = ['', '--help']
        rc = main(args)
        self.assertEqual(MbtaErrorCodes.Success, rc)

if __name__ == '__main__':
    unittest.main()
