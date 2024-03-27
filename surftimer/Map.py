from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery
from globals import get_cache, set_cache
from pydantic import BaseModel, validator
import simplejson as json
import time, datetime, surftimer.queries


router = APIRouter()


class MapModel(BaseModel):
    """Body for adding or updating **Map** entry"""

    id: int = None
    mapname: str
    author: str = "Unknown"
    tier: int
    stages: int
    bonuses: int = 0
    ranked: int = 0
    date_added: int = None
    last_played: int = None

    @validator("date_added", "last_played", pre=True, always=True)
    def default_timestamp(cls, v):
        """Automatically add the `UNIX` timestamps so we don't need to include them in the Body of the API call"""
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


@router.get(
    "/surftimer/mapinfo",
    name="Get Map Info",
    tags=["Map"],
)
async def selectMapInfo(
    request: Request,
    response: Response,
    mapname: str,
):
    """`Task<MySqlDataReader> reader = DB.Query($"SELECT * FROM Maps WHERE name='{MySqlHelper.EscapeString(Name)}'");`"""
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

    return xquery


@router.post(
    "/surftimer/insertmap",
    name="Insert Map",
    tags=["Map"],
)
async def insertMap(
    request: Request,
    response: Response,
    data: MapModel,
):
    """```c
    Task<int> writer = DB.Write($"INSERT INTO Maps (name, author, tier, stages, ranked, date_added, last_played) VALUES ('{MySqlHelper.EscapeString(Name)}', 'Unknown', {this.Stages}, {this.Bonuses}, 0, {(int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()}, {(int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()})");
    ....
    ```
    `date_added` and `last_played` values are automatically populated from the API as UNIX timestamps
    """
    tic = time.perf_counter()

    # print(data)
    # return data

    xquery = insertQuery(
        surftimer.queries.sql_insertMap.format(
            data.mapname,
            data.author,
            data.tier,
            data.stages,
            data.ranked,
            data.date_added,
            data.last_played,
        )
    )

    content_data = {"inserted": xquery, "xtime": time.perf_counter() - tic}
    if xquery < 1:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return response

    # Prepare the response
    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")

    response.body = json.dumps(content_data).encode("utf-8")
    response.status_code = status.HTTP_201_CREATED
    return response


@router.put(
    "/surftimer/updateMap",
    name="Update Map",
    tags=["Map"],
)
async def updateMapTier(
    request: Request,
    response: Response,
    data: MapModel,
):
    """```c
    $"UPDATE Maps SET last_played={(int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()}, stages={this.Stages}, bonuses={this.Bonuses} WHERE id={this.ID}";
    ....
    ```
    This is a single endpoint to update the data of the map, we will always update `stages`, `bonuses` values (full update) instead of the current way the plugin does it (full or partial update).\n
    `last_played` value is automatically populated from the API as UNIX timestamp.\n
    `id` is required here.
    """
    tic = time.perf_counter()

    # print(data)
    # return data

    xquery = insertQuery(
        surftimer.queries.sql_updateMap.format(
            data.last_played,
            data.stages,
            data.bonuses,
            data.id,
        )
    )

    content_data = {"updated": xquery, "xtime": time.perf_counter() - tic}
    if xquery < 1:
        # response.body = json.dumps(content_data).encode('utf-8')
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return response

    # Prepare the response
    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")

    response.body = json.dumps(content_data).encode("utf-8")
    response.headers["content-type"] = "application/json"
    response.status_code = status.HTTP_200_OK
    return response


@router.get(
    "/surftimer/maprunsdata",
    name="Get Map Runs Data",
    tags=["Map"],
)
async def selectMapRunsData(
    request: Request,
    response: Response,
    id: int,
    style: int,
    type: int,
):
    """
    # **Type** is now required
    ```
    // Get map world records
    Task<MySqlDataReader> reader = DB.Query($@"
        SELECT MapTimes.*, Player.name
        FROM MapTimes
        JOIN Player ON MapTimes.player_id = Player.id
        WHERE MapTimes.map_id = {this.ID} AND MapTimes.style = {style}
        ORDER BY MapTimes.run_time ASC;
    ");
    ```
    Will return a `List` of JSON objects for all the runs on the given **MapID**, **Style** and **Type** combo.\n
    This also includes the `Checkpoints` data for each of the runs.
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"selectMapRunsData:{id}-{style}-{type}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(surftimer.queries.sql_getMapRunsData.format(id, style, type))

    if xquery:
        xquery = xquery
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    if type == 0:  # 0 = map times
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
