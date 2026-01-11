import json
import logging

from fastapi import FastAPI, Depends, APIRouter
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from apis.passenger_update import api as passenger_update_api

from app.middleware import function_context

def create_app(router: APIRouter, title: str, version: str = "0.1.0") -> FastAPI:
    fast_app = FastAPI(title=title, version=version, dependencies=[Depends(function_context)])
    fast_app.include_router(passenger_update_api.router)

    fast_app.state.eventhub_clients = {}

    @fast_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_json = json.loads(exc.json())

        logging.warning(f"ValidationError occured, Error={exc_json}")

        return JSONResponse(exc_json, status_code=422)

    return fast_app