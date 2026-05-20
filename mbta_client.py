import os
import requests
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