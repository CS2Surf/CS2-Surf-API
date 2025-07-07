from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery
from globals import get_cache, set_cache
import simplejson as json
import time, datetime, surftimer.queries
from models import *
from typing import List, Dict, Any


router = APIRouter()


@router.get(
    "/surftimer/runbyplayer",
    name="Get Map Run By Player",
    tags=["Personal Best", "Player Stats"],
    summary="All the runs for the given **PlayerID, MapID, Type, Style** combo.",
    response_model=List[Dict[str, Any]],
)
async def selectRunByPlayer(
    request: Request,
    response: Response,
    player_id: int,
    map_id: int,
    type: int,
    style: int,
):
    """
    ```
        LoadPersonalBestRunAsync
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectRunByPlayer:{player_id}-{map_id}-{type}-{style}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getRunByPlayer.format(player_id, map_id, type, style)
    )

    if not xquery:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")
    return xquery


@router.get(
    "/surftimer/runbyid",
    name="Get Map Run By ID",
    tags=["Personal Best"],
    summary="Get a specific **MapTime ID**",
    response_model=Dict[str, Any],
)
async def selectRunById(
    request: Request,
    response: Response,
    run_id: int,
):
    """
    ```
        LoadPersonalBestRunAsync
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectRunById:{run_id}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(surftimer.queries.sql_getRunById.format(run_id))

    if xquery:
        xquery = xquery.pop()
    else:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")
    return xquery
