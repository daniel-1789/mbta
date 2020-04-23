import requests
import yaml
import sys
from enum import Enum

class MbtaErrorCodes(Enum):
    Success = 0
    NoOutput = 1
    Non200Resp = 2
    NoArgs = 3
    BadArgs = 4

def print_all_lines(get_routes_url):
    """
    Query the mbta api to get a list of the ids and names of all subway lines
    :param get_routes_url: api url for routes (made a param for unit testing to force failure)
    :return: MbtaErrorCodes enum - Success, NoOutput (200 response but no data), Non200Resp
    """
    rc = MbtaErrorCodes.Success
    # adjust the payload to only have what we need, sort it by id
    payload = {'filter[type]': '0,1', 'fields[route]': 'long_name,id', 'sort': 'id'}
    resp = requests.get(get_routes_url, payload)
    if resp.status_code != 200:
        # This means something went wrong.
        print('Problem getting data from MBTA. Please try again or contact support.')
        return MbtaErrorCodes.Non200Resp

    lines_json_dict = resp.json()
    if len(lines_json_dict) == 0:
        return MbtaErrorCodes.NoOutput
    for curr_line in lines_json_dict['data']:
        line_id = curr_line['id']
        line_name = curr_line['attributes']['long_name']
        print('ID: {}, NAME: {}'.format(line_id, line_name))
    return MbtaErrorCodes.Success

def print_stops(get_stops_url, line_id):
    """
    Query the mbta api to get a list of all the stops for the given line_id
    :param get_stops_url: api url (made a param for unit testing to force failure)
    :param line_id: string representing id of a line (i.e. Red, Green-B, etc.)
    :return: MbtaErrorCodes enum - Success, NoOutput (200 response but no data), Non200Resp
    """

    # adjust the payload to only have what we need, filter by line. Do not sort as data is in correct order
    payload = {'filter[route]': line_id, 'fields[stop]': 'name'}

    resp = requests.get(get_stops_url, payload)

    if resp.status_code != 200:
        # This means something went wrong.
        print('Problem getting data from MBTA. Please try again or contact support.')
        return MbtaErrorCodes.Non200Resp

    stops_json_dict = resp.json()
    if len(stops_json_dict['data']) == 0:
        print('No stops found for line ID \'{}\'. Please verify the line ID and remember they are case-sensitive'.format(line_id))
        return MbtaErrorCodes.NoOutput

    for curr_stop in stops_json_dict['data']:
        stop_name = curr_stop['attributes']['name']
        print(stop_name)

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
