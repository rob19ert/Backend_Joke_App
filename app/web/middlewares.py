import json
import typing

import jwt
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp.web_exceptions import HTTPException, HTTPUnprocessableEntity, HTTPUnauthorized

from app.store.crm.accessor import JWT_SECRET
from app.web.utils import error_json_response, json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application
HTTP_ERROR_CODES = {
    400: "bad request",
    401: "unauthorized",
    403: "forbidden",
    404: "notfound",
    405: "method_not_allowed",
    409: "conflict",
    500: "internal server error",
}
@middleware
async def error_handling_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(http_status=400, status="bad request", message=e.reason, data=json.loads(e.body))
    except HTTPException as e:
        return error_json_response(http_status=e.status, status=HTTP_ERROR_CODES[e.status], message=str(e))
    except Exception as e:
        return error_json_response(http_status=500, status="internal server error", message=str(e))


@middleware
async def auth_middleware(request, handler):
    if "Authorization" not in request.headers:
        if request.method == "GET" or request.path in ["/register_user", "/login"]:
            return await handler(request)
        raise HTTPUnauthorized(text="Authorization required")

    token = request.headers["Authorization"].split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPUnauthorized(text="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPUnauthorized(text="Invalid token")

    request["user"] = payload
    return await handler(request)

def setup_middleware(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(validation_middleware)
