import redis, time
import simplejson as json
from decimal import Decimal
from fastapi.security import HTTPBearer
from fastapi import Request
from datetime import datetime


token_auth_scheme = HTTPBearer()

# Config
with open("config.json", "r") as f:
    config = json.load(f)

# Requests Log
with open("requests.json") as fp:
    log = json.load(fp)

# Denied Log
with open("denied.json") as fd:
    denied = json.load(fd)


# Initiate Redis connection
redis_client = redis.Redis(
    host=config["REDIS"]["HOST"],
    port=config["REDIS"]["PORT"],
    password=config["REDIS"]["PASSWORD"],
)

tags_metadata = [
    {
        "name": "Map",
        "description": "All queries from the `Map.cs` file.",
    },
]

# Whitelisted IPs
WHITELISTED_IPS = config["WHITELISTED_IPS"]

# All styles
# 0 = normal, 1 = SW, 2 = HSW, 3 = BW, 4 = Low-Gravity, 5 = Slow Motion, 6 = Fast Forward, 7 = Freestyle
all_styles = [
    "Normal",
    "Sideways",
    "Half-Sideways",
    "Backwards",
    "Low-Gravity",
    "Slow Motion",
    "Fast Forward",
    "Freestyle",
]


def append_request_log(request: Request):
    """Logs some general info about the request recieved in `requests.json`"""
    log.append(
        {
            "url": str(request.url),
            "ip": request.client.host,
            "method": request.method,
            "headers": dict(request.headers),
            "time": str(datetime.now()),
        }
    )
    with open("requests.json", "w") as json_file:
        json.dump(log, json_file, indent=4, separators=(",", ": "))


def append_denied_log(request: Request):
    """Logs some general info about the denied request recieved in `denied.json`"""
    denied.append(
        {
            "url": str(request.url),
            "ip": request.client.host,
            "method": request.method,
            "cookies": request.cookies,
            "headers": dict(request.headers),
            "time": str(datetime.now()),
        }
    )
    with open("denied.json", "w") as json_file:
        json.dump(denied, json_file, indent=4, separators=(",", ": "))


def set_cache(cache_key: str, data):
    """Cache the data in Redis\n
    `Decimal` values are converted to `String`\n
    ### Still returns `True` if Redis functionality is disabled"""
    if config["REDIS"]["ENABLED"] == 0:
        return True

    redis_client.set(
        cache_key,
        json.dumps(
            data,
            use_decimal=True,
            encoding="utf-8",
            ensure_ascii=False,
            default=default_serializer,
            allow_nan=True,
        ),
        ex=config["REDIS"]["EXPIRY"],
    )

    return True


def get_cache(cache_key: str):
    """Try and get cached data from Redis\n
    ### Still returns `None` if Redis functionality is disabled"""
    if config["REDIS"]["ENABLED"] == 0:
        return None

    cached_data = redis_client.get(cache_key)
    if cached_data:
        # Return cached data
        return cached_data
    else:
        return None


def ordinal(n):
    suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    return str(n) + suffix


def custom_date_format(dt):
    day = ordinal(dt.day)
    month = dt.strftime("%B")
    year = dt.year
    time = dt.strftime("%H:%M:%S")
    return f"{day} of {month} {year}, {time}"


def custom_time_format(time_value):
    # Convert to Decimal for precise arithmetic
    time_value = Decimal(time_value)

    # Calculate minutes and remaining seconds
    minutes = int(time_value // 60)
    seconds = time_value % 60

    # Format the time
    formatted_time = f"{minutes}:{seconds:06.4f}" if minutes > 0 else f"{seconds:.4f}"

    return formatted_time


def default_serializer(obj):
    if isinstance(obj, datetime):
        return custom_date_format(obj)
    elif isinstance(obj, Decimal):
        return custom_time_format(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_decimal(obj):
    """Convert all instances of `Decimal` to `String`
    `"runtime": 14.7363` becomes `"runtime": "14.736300"`
    `"runtime": 11.25` becomes `"runtime": "11.250000"`"""
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], dict):
                for key, value in obj[i].items():
                    if isinstance(value, Decimal):
                        obj[i][key] = str(value)
        return obj
    # If it's neither a Decimal nor a list of dictionaries, return it as is
    return str(obj)
