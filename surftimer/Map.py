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
    "/surftimer/mapinfo",
    name="Get Map Info",
    tags=["Map"],
    summary="All map info available for the map",
    response_model=MapInfoModel,
)
async def selectMapInfo(
    request: Request,
    response: Response,
    mapname: str,
):
    """
    ```
        GetMapInfoAsync
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapInfo:{mapname}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(surftimer.queries.sql_getMapInfo.format(mapname))

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

    response_data = MapInfoModel(**xquery).model_dump()

    return JSONResponse(content=response_data)


@router.post(
    "/surftimer/insertmap",
    name="Insert Map",
    tags=["Map"],
    response_model=PostResponseData,
    summary="Adds a new map entry",
)
async def insertMap(
    request: Request,
    response: Response,
    data: MapInfoModel,
):
    """
    ```
        InsertMapInfoAsync
    ```
    `date_added` and `last_played` values are automatically populated from the API as UNIX timestamps
    """
    tic = time.perf_counter()

    xquery = insertQuery(
        surftimer.queries.sql_insertMap.format(
            data.name,
            data.author,
            data.tier,
            data.stages,
            data.bonuses,
            data.ranked,
            data.date_added,
            data.last_played,
        )
    )
    row_count, last_inserted_id = xquery

    content_data = PostResponseData(
        inserted=row_count, xtime=time.perf_counter() - tic, last_id=last_inserted_id
    )
    if row_count < 1:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return response

    # Prepare the response
    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")

    response.headers["content-type"] = "application/json"
    response.body = json.dumps(content_data.model_dump()).encode("utf-8")
    response.status_code = status.HTTP_201_CREATED
    return response


@router.put(
    "/surftimer/updateMap",
    name="Update Map",
    tags=["Map"],
    response_model=PostResponseData,
    summary="This is a single endpoint to update the data of the map, we will always update `stages`, `bonuses` values (full update) instead of the current way the plugin does it (full or partial update).",
)
async def updateMapTier(
    request: Request,
    response: Response,
    data: MapInfoModel,
):
    """
    # **id** is required here (maptime_id)
    ```
        UpdateMapInfoAsync
    ```
    `last_played` value is automatically populated from the API as UNIX timestamp.\n
    """
    tic = time.perf_counter()

    xquery = insertQuery(
        surftimer.queries.sql_updateMap.format(
            data.last_played,
            data.stages,
            data.bonuses,
            data.id,
        )
    )
    row_count, last_inserted_id = xquery

    content_data = PostResponseData(
        inserted=row_count, xtime=time.perf_counter() - tic, last_id=last_inserted_id
    )
    if row_count < 1:
        # response.body = json.dumps(content_data).encode('utf-8')
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return response

    # Prepare the response
    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")

    response.body = json.dumps(content_data.model_dump()).encode("utf-8")
    response.headers["content-type"] = "application/json"
    response.status_code = status.HTTP_200_OK
    return response


@router.get(
    "/surftimer/maprunsdata",
    name="Get Map Runs Data",
    tags=["Map"],
    summary="All the runs for the given **MapID**.",
    response_model=List[Dict[str, Any]],
)
async def selectMapRunsData(
    request: Request,
    response: Response,
    id: int,
    # style: int,
    # type: int,
):
    """
    ```
        GetMapRecordRunsAsync
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapRunsData:{id}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    # xquery = selectQuery(surftimer.queries.sql_getMapRunsData.format(id, style, type))
    xquery = selectQuery(surftimer.queries.sql_getMapRunsData.format(id))

    if not xquery:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")
    return xquery


@router.get(
    "/surftimer/maptotals",
    name="Get Map Record and Totals",
    tags=["Map"],
    summary="All map records and totals for the given **MapID** and **Style** combo.",
)
async def selectMapRecordAndTotals(
    request: Request,
    response: Response,
    map_id: int,
    style: int = 0,
):
    """
    ***NOT USED*** in plugin
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapRecordAndTotals:{map_id}-{style}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getMapRecordAndTotals.format(map_id, style)
    )

    if not xquery:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery


@router.get(
    "/surftimer/mapcheckpointsdata",
    name="Get Map Checkpoints Data",
    tags=["Map", "Personal Best"],
    summary="All map checkpoints data for the given **MapTime_ID**.",
    response_model=List[Dict[str, Any]],
)
async def selectMapCheckpointsData(
    request: Request,
    response: Response,
    maptime_id: int,
):
    """
    ```
        LoadCheckpointsAsync
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapCheckpointsData:{maptime_id}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(surftimer.queries.sql_getMapCheckpointsData.format(maptime_id))

    if not xquery:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery
