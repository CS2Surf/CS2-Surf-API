from pydantic import BaseModel, validator
from decimal import Decimal
from typing import List, Optional
import datetime


class PostResponeData(BaseModel):
    """Response body for POST (INSERT) actions"""

    inserted: int
    xtime: float
    last_id: Optional[int] = None
    trx: Optional[int] = None


class Checkpoint(BaseModel):
    """Body for adding or updating **Checkpoints** table entry"""

    cp: int
    ticks: int
    start_vel_x: Decimal
    start_vel_y: Decimal
    start_vel_z: Decimal
    end_vel_x: Decimal
    end_vel_y: Decimal
    end_vel_z: Decimal
    end_touch: int
    attempts: int


class CurrentRun(BaseModel):
    """Body for adding or updating **MapTimes** table entry"""

    player_id: int
    map_id: int
    run_time: int
    start_vel_x: Decimal
    start_vel_y: Decimal
    start_vel_z: Decimal
    end_vel_x: Decimal
    end_vel_y: Decimal
    end_vel_z: Decimal
    style: int = 0
    type: int = 0
    stage: int = 0
    checkpoints: List[Checkpoint] = None
    replay_frames: str
    run_date: Optional[int] = None

    @validator("run_date", pre=True, always=True)
    def default_timestamp(cls, v):
        """Automatically add the `UNIX` timestamps so we don't need to include them in the Body of the API call"""
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


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