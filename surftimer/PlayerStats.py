from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery
from globals import get_cache, set_cache
from typing import List, Dict, Any
import simplejson as json
import time, surftimer.queries

router = APIRouter()


@router.get(
    "/surftimer/playermapdata",
    name="Get Player Map Data - All runs",
    tags=["Player Stats"],
    summary="Combines `LoadMapTimesData` and `LoadCheckpointsData` queries into a single endpoint",
    response_model=List[Dict[str, Any]],
)
async def getPlayerMapData(
    request: Request,
    response: Response,
    player_id: int,
    map_id: int,
):
    """
    # **All** data for the player runs on a map.

    ```
        GetPlayerMapTimesAsync
    ```
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


@router.get(
    "/surftimer/playerspecificdata",
    name="Get specific data for a player run on a map",
    tags=["Player Stats"],
    summary="With this we can get the data for a specific type and style of run on a map. For example if we only need the stage runs, we specify the type as 2",
    response_model=List[Dict[str, Any]],
)
async def getPlayerSpecificData(
    request: Request,
    response: Response,
    player_id: int,
    map_id: int,
    style: int,
    type: int,
):
    """
    # NOT USED

    # **Type** mapping/logic:
    ## 0 = map time;
    ## 1 = bonus time (`stage` signifies bonus number);
    ## 2 = stage time (`stage` signifies stage number);
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"getPlayerSpecificData:{player_id}-{map_id}-{style}-{type}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getSpecificPlayerStatsData.format(
            player_id, map_id, style, type
        )
    )

    if xquery:
        xquery = xquery
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    if type == 0:
        for (
            item
        ) in (
            xquery
        ):  # Technically we would only have one item in this list as a player can only have 1 entry for the `type` and `style` combo
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


@router.get(
    "/surftimer/getmaprunbyrank",
    name="Get The Specified Rank Map Run Data",
    tags=["Player Stats"],
    summary="Get the run data for the specified rank on the map.",
    response_model=Dict[str, Any],
)
async def selectMapRunByRank(
    request: Request,
    response: Response,
    map_id: int,
    style: int,
    rank: int,
):
    """
    # NOT USED

    Gets the map run data for the specified rank on the specified map and style.
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapRunByRank:{map_id}-{style}-0-0-{rank}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getDataByRank.format(map_id, style, 0, 0, rank)
    )

    if not xquery:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        for (
            item
        ) in (
            xquery
        ):  # Technically we would only have one item in this list as a player can only have 1 entry for the `type` and `style` combo
            # Execute query to fetch checkpoints using the id from the current item
            checkpoints = selectQuery(
                surftimer.queries.sql_getMapCheckpointsData.format(item["id"])
            )

            # Append checkpoints to the current item
            item["checkpoints"] = checkpoints
        xquery = xquery.pop()

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery


@router.get(
    "/surftimer/getbonusrunbyrank",
    name="Get The Specified Rank Bonus Run Data",
    tags=["Player Stats"],
    summary="Get the bonus run data for the specified rank on the map.",
    response_model=Dict[str, Any],
)
async def selectBonusRunByRank(
    request: Request,
    response: Response,
    map_id: int,
    style: int,
    rank: int,
    bonus: int,
):
    """
    # NOT USED

    Gets the bonus run data for the specified rank on the specified map and style.
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectBonusRunByRank:{map_id}-{style}-1-{bonus}-{rank}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getDataByRank.format(map_id, style, 1, bonus, rank)
    )

    if not xquery:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        xquery = xquery.pop()

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery


@router.get(
    "/surftimer/getstagerunbyrank",
    name="Get The Specified Rank Stage Run Data",
    tags=["Player Stats"],
    summary="Get the stage run data for the specified rank on the map.",
    response_model=Dict[str, Any],
)
async def selectStageRunByRank(
    request: Request,
    response: Response,
    map_id: int,
    style: int,
    rank: int,
    stage: int,
):
    """
    # NOT USED

    Gets the stage run data for the specified rank on the specified map and style.
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectStageRunByRank:{map_id}-{style}-2-{stage}-{rank}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(
        surftimer.queries.sql_getDataByRank.format(map_id, style, 2, stage, rank)
    )

    if not xquery:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    else:
        xquery = xquery.pop()

    # Cache the data in Redis
    set_cache(cache_key, xquery)

    toc = time.perf_counter()

    print(f"Execution time {toc - tic:0.4f}")

    return xquery
