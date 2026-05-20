import os
import requests
import yaml
import sys
from enum import Enum
import httpx

# MBTA API key from env (unauthenticated callers are rate-limited to 20 req/min;
# a registered key raises this to 1000 req/min). Register at https://api-v3.mbta.com/register
_API_KEY = os.environ.get('MBTA_API_KEY')
_HEADERS = {'x-api-key': _API_KEY} if _API_KEY else {}


class MbtaUpstreamError(Exception):
    """Raised when the MBTA API returns a non-200 response."""
    pass

class MbtaNotFoundError(Exception):
    """Raised when the MBTA API returns 200 but no matching data."""
    pass


class MbtaErrorCodes(Enum):
    Success = 0
    NoOutput = 1
    Non200Resp = 2
    NoArgs = 3
    BadArgs = 4


_LINE_FIELDS = 'long_name,short_name,color,text_color,description,type,direction_names,direction_destinations'


def _line_row(r):
    a = r['attributes']
    return {
        'id': r['id'],
        'long_name': a['long_name'],
        'short_name': a['short_name'],
        'color': a['color'],
        'text_color': a['text_color'],
        'description': a.get('description'),
        'type': a['type'],
        'direction_names': a['direction_names'],
        'direction_destinations': a['direction_destinations'],
    }


def fetch_lines(get_routes_url):
    """
    Fetch all subway lines from MBTA. Returns list of line-detail dicts.
    Raises MbtaUpstreamError on non-200.
    """
    payload = {'filter[type]': '0,1', 'fields[route]': _LINE_FIELDS, 'sort': 'id'}
    resp = requests.get(get_routes_url, payload, headers=_HEADERS)
    if resp.status_code != 200:
        raise MbtaUpstreamError('MBTA returned status {}'.format(resp.status_code))
    data = resp.json().get('data', [])
    return [_line_row(r) for r in data]


async def async_fetch_lines(get_routes_url):
    """
    Async version of fetch_lines, for use inside an event loop (e.g., FastAPI).
    Same return shape and exception contract as fetch_lines.
    """
    payload = {'filter[type]': '0,1', 'fields[route]': _LINE_FIELDS, 'sort': 'id'}
    async with httpx.AsyncClient() as client:
        resp = await client.get(get_routes_url, params=payload, headers=_HEADERS)
    if resp.status_code != 200:
        raise MbtaUpstreamError('MBTA returned status {}'.format(resp.status_code))
    data = resp.json().get('data', [])
    return [_line_row(r) for r in data]


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
        print('ID: {}, NAME: {}'.format(line['id'], line['long_name']))
    return MbtaErrorCodes.Success


def fetch_stops(get_stops_url, line_id):
    """
    Fetch stops for a given line. Returns list of {'id', 'name'} dicts.
    Raises MbtaUpstreamError on non-200, MbtaNotFoundError if no stops found.
    """
    payload = {'filter[route]': line_id, 'fields[stop]': 'name'}
    resp = requests.get(get_stops_url, payload, headers=_HEADERS)
    if resp.status_code != 200:
        raise MbtaUpstreamError('MBTA returned status {}'.format(resp.status_code))
    data = resp.json().get('data', [])
    if not data:
        raise MbtaNotFoundError("No stops found for line '{}'".format(line_id))
    return [{'id': s['id'], 'name': s['attributes']['name']} for s in data]

async def async_fetch_stops(get_stops_url, line_id):
    """
    Async version of fetch_stops.
    """
    payload = {'filter[route]': line_id, 'fields[stop]': 'name'}
    async with httpx.AsyncClient() as client:
        resp = await client.get(get_stops_url, params=payload, headers=_HEADERS)
    if resp.status_code != 200:
        raise MbtaUpstreamError('MBTA returned status {}'.format(resp.status_code))
    data = resp.json().get('data', [])
    if not data:
        raise MbtaNotFoundError("No stops found for line '{}'".format(line_id))
    return [{'id': s['id'], 'name': s['attributes']['name']} for s in data]


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
        print("No stops found for line ID '{}'. Please verify the line ID and remember they are case-sensitive".format(
            line_id))
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
    # get the api urls from the mbta.yaml, make sure all the proper keys are present.
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
