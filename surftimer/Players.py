from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery
from globals import get_cache, set_cache
import simplejson as json
import time, datetime, surftimer.queries
from models import *


router = APIRouter()


@router.get(
    "/surftimer/playersurfprofile/{steamid}",
    name="Get Player Profile",
    tags=["Player Profile"],
    summary="All player profile information",
    response_model=PlayerSurfProfile,
)
async def getPlayerProfileData(
    request: Request,
    response: Response,
    steamid: int,
):
    """
    ```
    Task<MySqlDataReader> dbTask = DB.Query($"SELECT * FROM `Player` WHERE `steam_id` = {player.SteamID} LIMIT 1;");
    ```
    """
    tic = time.perf_counter()

    # Check if data is cached in Redis
    cache_key = f"getPlayerProfileData:{steamid}"
    cached_data = get_cache(cache_key)
    if cached_data is not None:
        print(f"[Redis] Loaded '{cache_key}' ({time.perf_counter() - tic:0.4f}s)")
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_200_OK
        response.body = json.loads(cached_data, use_decimal=True, parse_nan=True)
        return response

    xquery = selectQuery(surftimer.queries.sql_getPlayerProfileData.format(steamid))

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

    response_data = PlayerSurfProfile(**xquery).model_dump()
    return JSONResponse(content=response_data)


@router.post(
    "/surftimer/insertplayer",
    name="Insert Player",
    tags=["Player Profile"],
    response_model=PostResponeData,
    summary="Adds a new player profile entry",
)
async def insertPlayer(
    request: Request,
    response: Response,
    data: PlayerSurfProfile,
):
    """
    ```c
    // Write new player to database
    Task<int> newPlayerTask = DB.Write($@"
        INSERT INTO `Player` (`name`, `steam_id`, `country`, `join_date`, `last_seen`, `connections`)
        VALUES ('{MySqlHelper.EscapeString(name)}', {player.SteamID}, '{country}', {joinDate}, {lastSeen}, {connections});
    ");
    ....
    ```
    `join_date` and `last_seen` values are automatically populated from the API as UNIX timestamps
    """
    tic = time.perf_counter()

    xquery = insertQuery(
        surftimer.queries.sql_insertPlayerProfile.format(
            data.name,
            data.steam_id,
            data.country,
            data.join_date,
            data.last_seen,
            data.connections,
        )
    )
    row_count, last_inserted_id = xquery

    content_data = PostResponeData(
        row_count, time.perf_counter() - tic, last_inserted_id
    )
    if row_count < 1:
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
    "/surftimer/updateplayerprofile",
    name="Update Player Profile",
    tags=["Player Profile"],
    response_model=PostResponeData,
    summary="Update the already existing player profile",
)
async def updatePlayerProfile(
    request: Request,
    response: Response,
    country: str,
    id: int,
):
    """```c
    // Update data in Player DB table
    Task<int> updatePlayerTask = DB.Write($@"
        UPDATE `Player` SET country = '{playerList[player.UserId ?? 0].Profile.Country}',
        `last_seen` = {(int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()}, `connections` = `connections` + 1
        WHERE `id` = {playerList[player.UserId ?? 0].Profile.ID} LIMIT 1;
    ");
    ....
    ```
    `last_played` value is automatically populated from the API as UNIX timestamp.\n
    `id` is required here.
    """
    tic = time.perf_counter()

    xquery = insertQuery(
        surftimer.queries.sql_updatePlayerProfile.format(
            country,
        )
    )
    row_count, last_inserted_id = xquery

    content_data = PostResponeData(
        row_count, time.perf_counter() - tic, last_inserted_id
    )
    if row_count < 1:
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
