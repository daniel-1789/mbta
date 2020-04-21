import requests
import yaml
import json

with open(r'mbta.yaml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    api_dict = yaml.load(file, Loader=yaml.FullLoader)


# https://api-v3.mbta.com/routes?filter%5Btype%5D=0,1
payload = {'filter[type]': '0,1', 'fields[route]': 'long_name,id', 'sort': 'id'}
resp = requests.get(api_dict['get_routes'], payload)
if resp.status_code != 200:
    # This means something went wrong.
    raise ()
lines_json_dict = resp.json()
for curr_line in lines_json_dict['data']:
    line_id = curr_line['id']
    line_name = curr_line['attributes']['long_name']
    print('ID: {}, NAME: {}'.format(line_id, line_name))


payload = {'filter[route]': 'Red', 'fields[stop]': 'name'}
resp = requests.get(api_dict['get_stops'], payload)
if resp.status_code != 200:
    # This means something went wrong.
    raise ()
stops_json_dict = resp.json()
for curr_stop in stops_json_dict['data']:
    stop_name = curr_stop['attributes']['name']
    print(stop_name)