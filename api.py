import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mbta import (
    async_fetch_lines,
    async_fetch_stops,
    MbtaUpstreamError,
    MbtaNotFoundError,
)

# Load API URLs once at startup. uvicorn runs from project root, so a relative
# path is fine here.
with open('mbta.yaml') as f:
    _API_URLS = yaml.safe_load(f)


class Line(BaseModel):
    id: str
    long_name: str


class LineDetail(Line):
    short_name: str
    color: str
    text_color: str
    description: str | None = None
    type: int
    direction_names: list[str]
    direction_destinations: list[str]


class Stop(BaseModel):
    id: str
    name: str


app = FastAPI(
    title="MBTA Service",
    description="HTTP wrapper around the MBTA v3 API",
    version="0.1.0",
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/lines", response_model=list[LineDetail])
async def get_lines():
    try:
        return await async_fetch_lines(_API_URLS['get_lines'])
    except MbtaUpstreamError as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/lines/{line_id}/stops", response_model=list[Stop])
async def get_stops_for_line(line_id: str):
    try:
        return await async_fetch_stops(_API_URLS['get_stops'], line_id)
    except MbtaUpstreamError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except MbtaNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))