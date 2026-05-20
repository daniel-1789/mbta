# mbta

A small Python wrapper around the [MBTA v3 API](https://api-v3.mbta.com/) that exposes Boston's subway lines and their stops two ways: as an HTTP service and as a CLI.

## Layout

| File | Purpose |
| --- | --- |
| `mbta_client.py` | Domain layer — sync + async fetchers and exception types. |
| `cli.py` | Command-line entry point. Calls into `mbta_client`. |
| `api.py` | FastAPI app — thin HTTP layer over `mbta_client`. |
| `mbta.yaml` | Upstream MBTA URLs, loaded at startup by both entry points. |
| `mbta_unit_test.py` | Unit tests for the CLI path. |
| `mbta` | Shell wrapper that invokes `python3 cli.py "$@"`. |
| `requirements.txt` | Pinned dependencies. |

## Install

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Optional: set `MBTA_API_KEY` in your environment to lift the upstream rate limit from 20 req/min to 1000 req/min. Register a key at <https://api-v3.mbta.com/register>.

## HTTP service

Launch with uvicorn from the project root (the app reads `mbta.yaml` relative to the working directory):

```shell
uvicorn api:app --reload
```

Interactive OpenAPI docs are served at `/docs`.

### Endpoints

| Method | Path | Returns |
| --- | --- | --- |
| `GET` | `/healthz` | `{"status": "ok"}` |
| `GET` | `/lines` | List of subway lines with full detail (id, names, color/text_color, type, direction names + destinations, description). |
| `GET` | `/lines/{line_id}/stops` | Ordered list of stops for the given line (`Red`, `Green-B`, etc.). |

Error handling:
- `502` if the MBTA upstream returns a non-200.
- `404` if the line id is unknown (no stops returned).

## CLI

```shell
python cli.py --get-lines
python cli.py --get-stops Red
python cli.py --help
```

Or via the shell wrapper (`./mbta --get-lines`). Exit/return codes are defined by `MbtaErrorCodes` in `cli.py`.

## Tests

```shell
python -m unittest mbta_unit_test.py
```

## Design notes

- The MBTA `/routes` and `/stops` responses are large; requests pin `fields[...]` to only what the models need, keeping payloads small.
- `mbta_client.py` exposes parallel sync/async fetchers (`fetch_lines` / `async_fetch_lines`, `fetch_stops` / `async_fetch_stops`) so the CLI can keep using `requests` while FastAPI uses `httpx` inside the event loop. Both share one row-mapping helper to keep the response shape consistent.
- Upstream errors raise `MbtaUpstreamError`; "found nothing for this line id" raises `MbtaNotFoundError`. The CLI catches these and prints user-facing messages; the API translates them into 502/404.
- Lines are sorted by id for stable output; stops are returned in the upstream's order, which matches the MBTA map ordering.