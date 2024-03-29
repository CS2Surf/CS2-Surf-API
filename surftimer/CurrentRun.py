from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse
from sql import selectQuery, insertQuery, executeTransaction
from globals import get_cache, set_cache
import simplejson as json
import time, surftimer.queries
from typing import List
from models import *


router = APIRouter()


@router.post(
    "/surftimer/savemaptime",
    name="Save Map Time",
    tags=["Current Run"],
    response_model=PostResponseData,
    summary="Combines `SaveMapTime` and `SaveCurrentRunCheckpoints`",
)
async def saveMapTime(
    request: Request,
    response: Response,
    data: CurrentRun,
):
    """
    `run_date` value is automatically populated from the API as UNIX timestamp
    """
    tic = time.perf_counter()

    # print(data)
    # return data

    xquery = insertQuery(
        surftimer.queries.sql_insertMapTime.format(
            data.player_id,
            data.map_id,
            data.style,
            0, # Hardcoding type = 0 to signify that this is a Map Run Time
            data.stage,
            data.run_time,
            data.start_vel_x,
            data.start_vel_y,
            data.start_vel_z,
            data.end_vel_x,
            data.end_vel_y,
            data.end_vel_z,
            data.run_date,
            data.replay_frames,
        )
    )
    row_count, last_inserted_id = xquery

    # Now we have the `maptime_id` here we will add the checkpoints
    checkpoint_queries = []
    for checkpoint in data.checkpoints:
        cpquery = surftimer.queries.sql_insertCheckpoint.format(
            last_inserted_id,
            checkpoint.cp,
            checkpoint.run_time,
            checkpoint.start_vel_x,
            checkpoint.start_vel_y,
            checkpoint.start_vel_z,
            checkpoint.end_vel_x,
            checkpoint.end_vel_y,
            checkpoint.end_vel_z,
            checkpoint.attempts,
            checkpoint.end_touch,
        )

        checkpoint_queries.append(cpquery)

    # Start the transaction with all checkpoints
    trx = executeTransaction(checkpoint_queries)

    content_data = PostResponseData(
        inserted=row_count, xtime=time.perf_counter() - tic, last_id=last_inserted_id, trx=trx
    )
    if row_count < 1:
        response.headers["content-type"] = "application/json"
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return response

    # Prepare the response
    toc = time.perf_counter()
    print(f"Execution time {toc - tic:0.4f}")

    response.body = json.dumps(content_data.model_dump()).encode("utf-8")
    response.status_code = status.HTTP_201_CREATED
    return response


@router.post(
    "/surftimer/savestagetime",
    name="Save Stage Time",
    tags=["Current Run"],
    response_model=PostResponseData,
    summary="Saves a stage run time",
)
async def saveStageTime(
    request: Request,
    response: Response,
    data: CurrentRun,
):
    """
    `run_date` value is automatically populated from the API as UNIX timestamp
    `checkpoints` value is **NOT** required here
    """
    tic = time.perf_counter()

    # print(data)
    # return data

    xquery = insertQuery(
        surftimer.queries.sql_insertMapTime.format(
            data.player_id,
            data.map_id,
            data.style,
            2,  # Hardcoding type = 2 to signify that this is a Stage Run Time
            data.stage,
            data.run_time,
            data.start_vel_x,
            data.start_vel_y,
            data.start_vel_z,
            data.end_vel_x,
            data.end_vel_y,
            data.end_vel_z,
            data.run_date,
            data.replay_frames,
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

    response.body = json.dumps(content_data.model_dump()).encode("utf-8")
    response.status_code = status.HTTP_201_CREATED
    return response

@router.post(
    "/surftimer/savebonustime",
    name="Save Bonus Time",
    tags=["Current Run"],
    response_model=PostResponseData,
    summary="Saves a bonus run time",
)
async def saveBonusTime(
    request: Request,
    response: Response,
    data: CurrentRun,
):
    """
    `run_date` value is automatically populated from the API as UNIX timestamp\n
    `checkpoints` value is **NOT** required here
    """
    tic = time.perf_counter()

    # print(data)
    # return data

    xquery = insertQuery(
        surftimer.queries.sql_insertMapTime.format(
            data.player_id,
            data.map_id,
            data.style,
            1,  # Hardcoding type = 1 to signify that this is a Bonus Run Time
            data.stage, # This represents the bonus number
            data.run_time,
            data.start_vel_x,
            data.start_vel_y,
            data.start_vel_z,
            data.end_vel_x,
            data.end_vel_y,
            data.end_vel_z,
            data.run_date,
            data.replay_frames,
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

    response.body = json.dumps(content_data.model_dump()).encode("utf-8")
    response.status_code = status.HTTP_201_CREATED
    return response
