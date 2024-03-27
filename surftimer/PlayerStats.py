from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery
from globals import get_cache, set_cache
from pydantic import BaseModel, validator
import simplejson as json
import time, surftimer.queries

router = APIRouter()


@router.get(
    "/surftimer/playermapdata",
    name="Get Player Map Data - All runs",
    tags=["Player Stats"],
)
async def getPlayerMapData(
    request: Request,
    response: Response,
    player_id: int,
    map_id: int,
):
    """
    # **All** data for the player runs on a map.
    \n\n
    Combines `LoadMapTimesData` and `LoadCheckpointsData` queries into a single endpoint
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"getPlayerMapData:{player_id}-{map_id}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getPlayerMapData.format(player_id, map_id)
    )

    if xquery:
        xquery = xquery
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    for item in xquery:
        # Execute query to fetch checkpoints using the id from the current item
        checkpoints = selectQuery(
            surftimer.queries.sql_getMapCheckpointsData.format(item["id"])
        )

        # Append checkpoints to the current item
        item["checkpoints"] = checkpoints

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery
