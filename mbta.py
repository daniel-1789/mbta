import requests
import yaml
import sys

def print_all_lines(get_routes_url):
    # adjust the payload to only have what we need, sort it by id
    payload = {'filter[type]': '0,1', 'fields[route]': 'long_name,id', 'sort': 'id'}
    resp = requests.get(get_routes_url, payload)
    if resp.status_code != 200:
        # This means something went wrong.
        print('Problem getting data from MBTA. Please try again or contact support.')
        return
    lines_json_dict = resp.json()
    for curr_line in lines_json_dict['data']:
        line_id = curr_line['id']
        line_name = curr_line['attributes']['long_name']
        print('ID: {}, NAME: {}'.format(line_id, line_name))

def print_stops(get_stops_url, line_id):
    # adjust the payload to only have what we need, filter by line. Do not sort as data is in correct order

    payload = {'filter[route]': line_id, 'fields[stop]': 'name'}

    resp = requests.get(get_stops_url, payload)
    if resp.status_code != 200:
        # This means something went wrong.
        print('Problem getting data from MBTA. Please try again or contact support.')
        return
    stops_json_dict = resp.json()
    if len(stops_json_dict['data']) == 0:
        print('No stops found for line ID \'{}\'. Please verify the line ID and remember they are case-sensitive'.format(line_id))
    else:
        for curr_stop in stops_json_dict['data']:
            stop_name = curr_stop['attributes']['name']
            print(stop_name)
    return len(stops_json_dict['data'])

def usage_message(custom_message=None):
    """
    Simple usage message.
    :return:
    """
    if custom_message is not None:
        print(custom_message)
    print('Usage: ')
    print('mbta --get-routes')
    print('mbta --get-stops route_id')
    print('mbta --help')

def main(args):
    with open(r'mbta.yaml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        api_dict = yaml.load(file, Loader=yaml.FullLoader)

    if len(args) < 2:
        usage_message('At least one option required')
    else:
        curr_arg = args[1]
        if curr_arg == '--get-routes':
            if len(args) != 2:
                usage_message('--get-routes has no parameters')
            else:
                print_all_lines(api_dict['get_routes'])
        elif curr_arg == '--get-stops':
            if len(args) != 3:
                usage_message('--get-stops requires a single parameter')
            else:
                line_id = args[2]
                print_stops(api_dict['get_stops'], line_id)
        else:
            usage_message()



if __name__ == "__main__":
    main(sys.argv)
