# IMPORTS
from datetime import datetime
from fastapi import FastAPI, Request, status, Depends, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware
from auth import VerifyToken
from threading import Thread  # Not used yet

# Templates
from fastapi.openapi.docs import get_swagger_ui_html

from globals import (
    token_auth_scheme,
    config,
    redis_client,
    tags_metadata,
    WHITELISTED_IPS,
    append_request_log,
    append_denied_log,
)


# Import all the endpoints for each table
from surftimer.Map import router as Map
from surftimer.PlayerStats import router as PlayerStats


class IPValidatorMiddleware(BaseHTTPMiddleware):
    """This will check whether the Request IP is in our `WHITELISTED_IPS` and let it through or return status code `400` if not in `WHITELISTED_IPS`"""
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        ip = str(request.client.host)

        # Check if IP is allowed
        if ip not in WHITELISTED_IPS:
            append_denied_log(request)
            data = {"message": "Not Allowed", "ip": ip}
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

        append_request_log(request)
        # Proceed if IP is allowed
        return await call_next(request)


# Swagger UI configuration - https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
swagger_config = {
    "displayOperationId": False,  # Show operationId on the UI
    "defaultModelsExpandDepth": 1,  # The default expansion depth for models (set to -1 completely hide the models)
    "defaultModelExpandDepth": 2,
    "defaultModelRendering": "example",
    "deepLinking": True,  # Enables deep linking for tags and operations
    "useUnsafeMarkdown": True,
    "displayRequestDuration": True,
    "filter": True,
    "showExtensions": True,
    "syntaxHighlight.theme": "arta",
    "docExpansion": "none",
    "pluginLoadType": "chain",
    "tagsSorter": "alpha",
}
app = FastAPI(
    title="CS2 SurfTimer API",
    description="""by [`tslashd`](https://github.com/tslashd)""",
    version="0.0.0",
    debug=True,
    swagger_ui_parameters=swagger_config,
    middleware=[Middleware(IPValidatorMiddleware)],
    openapi_tags=tags_metadata,
)


# Attach the routes
app.include_router(Map)
app.include_router(PlayerStats)


@app.get("/docs2", include_in_schema=False)
async def custom_swagger_ui_html_cdn():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        # swagger_ui_dark.css CDN link
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.min.css",
        swagger_ui_parameters=swagger_config,
    )


@app.get("/", include_in_schema=False)
async def home():
    data = {"message": "Suuuuh duuuud"}
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


# This is an example of a endpoint locked behind an AUTH token 👇
@app.get(
    "/api/private",
    tags=["Private"],
    name="Test Authentication Tokens",
    include_in_schema=False,
)
async def private(
    response: Response, token: str = Depends(token_auth_scheme)
):  # 👈 updated code
    """A valid access token is required to access this route"""

    result = VerifyToken(token.credentials).verify()  # 👈 updated code

    # 👇 new code
    if result.get("status"):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return result
    # 👆 new code

    dt = datetime.fromtimestamp(int(result["exp"]))
    formatted_datetime = dt.strftime("%H:%M:%S %d-%m-%Y")
    print("expiry:", formatted_datetime)

    return result
