import sys
import yaml
from enum import Enum

from mbta_client import (
    fetch_lines,
    fetch_stops,
    MbtaUpstreamError,
    MbtaNotFoundError,
)


class MbtaErrorCodes(Enum):
    Success = 0
    NoOutput = 1
    Non200Resp = 2
    NoArgs = 3
    BadArgs = 4


def print_all_lines(get_routes_url):
    """
    CLI helper: fetch lines and print them. Returns MbtaErrorCodes.
    """
    try:
        lines = fetch_lines(get_routes_url)
    except MbtaUpstreamError:
        print('Problem getting data from MBTA. Please try again or contact support.')
        return MbtaErrorCodes.Non200Resp
    if not lines:
        return MbtaErrorCodes.NoOutput
    for line in lines:
        print(f"ID: {line['id']}, NAME: {line['long_name']}")
    return MbtaErrorCodes.Success


def print_stops(get_stops_url, line_id):
    """
    CLI helper: fetch stops for a line and print them. Returns MbtaErrorCodes.
    """
    try:
        stops = fetch_stops(get_stops_url, line_id)
    except MbtaUpstreamError:
        print('Problem getting data from MBTA. Please try again or contact support.')
        return MbtaErrorCodes.Non200Resp
    except MbtaNotFoundError:
        print(f"No stops found for line ID '{line_id}'. Please verify the line ID and remember they are case-sensitive")
        return MbtaErrorCodes.NoOutput
    for stop in stops:
        print(stop['name'])
    return MbtaErrorCodes.Success


def usage_message(custom_message=None):
    """
    Simple usage message.
    :param custom_message: Any additional text beyond usage instructions
    :return:
    """
    if custom_message is not None:
        print(custom_message)
    print('Usage: ')
    print('mbta --get-lines')
    print('mbta --get-stops <line_id>')
    print('mbta --help')


def main(args):
    """
    Main function to take command line parameters and execute proper api calls for getting routes and stops
    :param args: argv from command line
    :return: MbtaErrorCodes - Success, NoArgs (no arguments passed), BadArgs (bad arguments passed or extra
        parameters given), or the results of the call to the MBTA API.
    """
    try:
        with open(r'mbta.yaml') as file:
            api_dict = yaml.load(file, Loader=yaml.FullLoader)
    except:
        print('Error - missing needed mbta.yaml file')
        raise

    try:
        api_dict['get_stops']
        api_dict['get_lines']
    except:
        print('Error - api_dict missing needed keys')
        raise

    if len(args) < 2:
        usage_message('At least one option required')
        return MbtaErrorCodes.NoArgs
    curr_arg = args[1]
    if curr_arg == '--get-lines':
        if len(args) != 2:
            usage_message('--get-routes has no parameters')
            return MbtaErrorCodes.BadArgs
        return print_all_lines(api_dict['get_lines'])
    elif curr_arg == '--get-stops':
        if len(args) != 3:
            usage_message('--get-stops requires a single parameter')
            return MbtaErrorCodes.BadArgs
        line_id = args[2]
        return print_stops(api_dict['get_stops'], line_id)
    elif curr_arg == '--help':
        usage_message()
        return MbtaErrorCodes.Success
    else:
        usage_message()
        return MbtaErrorCodes.BadArgs


if __name__ == "__main__":
    main(sys.argv)
