import datetime
import logging
import os
import asyncio

import json

from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Query, Request, Security
from fastapi.security.api_key import APIKeyHeader
from starlette import status
from app.middleware import FunctionContext, function_context
from dependencies.eventhub.eventhub_config import EventHubInstanceConfig, get_eventhub_instance_config
from dependencies.eventhub.eventhub_sender import EventHubSender
from dtos.flight_update_events import FlightUpdateEvent
from dtos.flight_schedule_events import FlightScheduleEvent
from dtos.flight_master_events import FlightMasterEvent
from helper.data_generation import generate_metadata
from helper.require_app_role import require_app_role
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from lxml import etree
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix='/api')

DATA_SOURCE_NAME = "AirportOperationalSystems"
AIP_FLIGHT_UPDATE_APP_ROLE = "AIP.FlightUpdate.Write"
PUBLISHER_NAME = "NIA AIP"

STORAGE_ACCOUNT_NAME = os.getenv("TRANSIENT_STORAGE_ACCOUNT_NAME")
FILE_SYSTEM_NAME = os.getenv("TRANSIENT_FILE_SYSTEM_NAME")
FLSH_DIRECTORY_NAME = "input/flsh"
MSTR_DIRECTORY_NAME = "input/mstr"
 
 
ns = {
    'yiapl': 'yiapl.co.in/root/schema',
    'aidx': 'http://www.iata.org/IATA/2007/00'
}

async def require_flight_update_write_app_role(bearer_token: str = Security(APIKeyHeader(name="Authorization", auto_error=True))):
    return require_app_role(app_role=AIP_FLIGHT_UPDATE_APP_ROLE, bearer_token=bearer_token)


def flight_update_eventhub_instance_config() -> EventHubInstanceConfig:
    return get_eventhub_instance_config("FLIGHT_UPDATES")

def normalize_xml_body(raw: bytes) -> bytes:
    UTF8_BOM = b"\xef\xbb\xbf"
    if raw.startswith(UTF8_BOM):
        raw = raw[len(UTF8_BOM):]

    raw_stripped = raw.strip()

    if raw_stripped.startswith(b'"') and raw_stripped.endswith(b'"'):
        text = json.loads(raw_stripped)
    else:
        text = raw.decode("utf-8", errors="strict")

    if not text.lstrip().startswith("<"):
        raise ValueError("Payload is not XML after normalization")

    return text.encode("utf-8")

@router.post(path="/flightupdate/v1",
             summary="Ingest new Flight Update",
             operation_id="post_flight_update_v1",
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(require_flight_update_write_app_role)])
async def flight_update_v1(
        request: Request,
        event_schema_version: Annotated[FlightUpdateEvent.SchemaVersionV1, Query(
        )] = FlightUpdateEvent.SchemaVersionV1.v1_0,
        context: FunctionContext = Depends(function_context),
        eventhub_sender: EventHubSender = Depends(),
        eventhub_config: EventHubInstanceConfig = Depends(
            flight_update_eventhub_instance_config) 
):
    logging.info(
        f"Function called, FunctionName={context.function_name}, InvocationId={context.invocation_id}")

    metadata = generate_metadata("flightUpdates",
                                 DATA_SOURCE_NAME,
                                 event_schema_version,
                                 datetime.datetime.utcnow(),
                                 context,
                                 PUBLISHER_NAME)

    try:
        content_type = request.headers.get('content-type')
        if content_type and 'xml' in content_type:

            raw = await request.body()

            try:
                body_bytes = normalize_xml_body(raw)
            except ValueError as ve:             
                logging.error(f"Failed to normalize XML payload: {str(ve)}")
                raise HTTPException(status_code=400, detail="Invalid XML format")
            
            await eventhub_sender.send_data(eventhub_config.eventhub_name, body_bytes, metadata)
            logging.info(
                f"Function payload, FunctionName={context.function_name}, InvocationId={context.invocation_id}: {body_bytes}")
        else:
            logging.error(f"Expected XML content-type, but received: {content_type}")
            raise HTTPException(status_code=400, detail="Expected XML content-type in request header")
    except Exception as e:
        if isinstance(e,HTTPException):
            raise e
        else:
            logging.exception(
                f"Error occured, FunctionName={context.function_name} with InvocationId={context.invocation_id}, "
                f"ExceptionType={type(e).__name__}, ExceptionMessage={str(e)}")
        raise HTTPException(status_code=500,
                            detail='An error occurred while ingesting the data. Please try again later.')

    return {'Status': 'Success'}
            
@router.post(path="/flightschedule/v1",
             summary="Ingest new Flight schedule",
             operation_id="post_flight_schedule_v1",
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(require_flight_update_write_app_role)])
async def flight_schedule_v1(
        request: Request,
        event_schema_version: Annotated[FlightScheduleEvent.SchemaVersionV1, Query(
        )] = FlightScheduleEvent.SchemaVersionV1.v1_0,
        context: FunctionContext = Depends(function_context)
):
    logging.info(
        f"Function called, FunctionName={context.function_name}, InvocationId={context.invocation_id}")
   
    metadata = generate_metadata("flightSchedule",
                                 DATA_SOURCE_NAME,
                                 event_schema_version,
                                 datetime.datetime.utcnow(),
                                 context,
                                 PUBLISHER_NAME)
   
    try:
        content_type = request.headers.get('content-type')
        if content_type and 'xml' in content_type:
            try:
                body = await request.body()
               
                logging.info(
                    f"Function payload, FunctionName={context.function_name}, InvocationId={context.invocation_id}: {body}")
               
                root = etree.fromstring(body)
                message_type = root.xpath('//yiapl:MessageType/text()', namespaces=ns)[0]
                message_subtype = root.xpath('//yiapl:MessageSubType/text()', namespaces=ns)[0]
            except Exception as e:
                logging.error(f"Failed to parse XML payload: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid XML format")

            file_name = generate_file_name(message_type,message_subtype,context.invocation_id)
            await write_message_to_datalake (file_name, body, FLSH_DIRECTORY_NAME,metadata)              
            
        else:
            logging.error(f"Expected XML content-type, but received: {content_type}")
            raise HTTPException(status_code=400, detail="Expected XML content-type in request header")
        
    except Exception as e:
        if isinstance(e,HTTPException):
            raise e
        else:
            logging.exception(
                f"Error occured, FunctionName={context.function_name} with InvocationId={context.invocation_id}, "
                f"ExceptionType={type(e).__name__}, ExceptionMessage={str(e)}")
            raise HTTPException(status_code=500,
                            detail='An error occurred while ingesting the data. Please try again later.')
 
    return {'Status': 'Success'}

@router.post(path="/flightmaster/v1",
             summary="Ingest new Flight master",
             operation_id="post_flight_master_v1",
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(require_flight_update_write_app_role)])
async def flight_master_v1(
        request: Request,
        event_schema_version: Annotated[FlightMasterEvent.SchemaVersionV1, Query(
        )] = FlightMasterEvent.SchemaVersionV1.v1_0,
        context: FunctionContext = Depends(function_context)
):
    logging.info(
        f"Function called, FunctionName={context.function_name}, InvocationId={context.invocation_id}")
   
    metadata = generate_metadata("flightMaster",
                                 DATA_SOURCE_NAME,
                                 event_schema_version,
                                 datetime.datetime.utcnow(),
                                 context,
                                 PUBLISHER_NAME)
 
    try:
        content_type = request.headers.get('content-type')
        if content_type and 'xml' in content_type:
            try:
                body = await request.body()
               
                logging.info(
                    f"Function payload, FunctionName={context.function_name}, InvocationId={context.invocation_id}: {body}")
               
                root = etree.fromstring(body)
                message_type = root.xpath('//yiapl:MessageType/text()', namespaces=ns)[0]
                message_subtype = root.xpath('//yiapl:MessageSubType/text()', namespaces=ns)[0]
            except Exception as e:
                logging.error(f"Failed to parse XML payload: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid XML format")

            file_name = generate_file_name(message_type,message_subtype,context.invocation_id)
            await write_message_to_datalake (file_name, body, MSTR_DIRECTORY_NAME,metadata)            
            
        else:
            logging.error(f"Expected XML content-type, but received: {content_type}")
            raise HTTPException(status_code=400, detail="Expected XML content-type in request header")
 
    except Exception as e:
        if isinstance(e,HTTPException):
            raise e
        else:
            logging.exception(
                f"Error occured, FunctionName={context.function_name} with InvocationId={context.invocation_id}, "
                f"ExceptionType={type(e).__name__}, ExceptionMessage={str(e)}")
            raise HTTPException(status_code=500,
                                detail='An error occurred while ingesting the data. Please try again later.')
    return {'Status': 'Success'}


_executor = ThreadPoolExecutor(max_workers=4)

async def write_message_to_datalake(file_name, message, directory_name, metadata):
    """
    Write message to Azure Data Lake Storage asynchronously.
    Uses run_in_executor for Python 3.8 compatibility.
    """
    def _write_to_datalake_sync():
        try:
            #service client using DefaultAzureCredential
            service_client = DataLakeServiceClient(
                account_url=f"https://{STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
                credential= DefaultAzureCredential()
            )

            # Get a file system client
            file_system_client = service_client.get_file_system_client(FILE_SYSTEM_NAME)
            directory_client = file_system_client.get_directory_client(directory_name)

            try:
                directory_client.get_directory_properties()
            except:
                directory_client.create_directory()
            
            file_client = directory_client.get_file_client(file_name)
            file_client.upload_data(
                data=message,
                overwrite=True,
                metadata=metadata
            )   
            logging.info(f"Message successfully written to {file_name} in {directory_name}/{FILE_SYSTEM_NAME}")
        
        except Exception as e:
            logging.info(f"An error occured while writing to {file_name} in {directory_name}/{FILE_SYSTEM_NAME} : {e}")
            raise e

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _write_to_datalake_sync)
            
    
    
def generate_file_name(message_type,message_subtype,invocation_id):
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    formatted_date = timestamp.strftime("%Y%m%d_%H%M%S")
    
    return f"{message_type}_{message_subtype}_{formatted_date}_{invocation_id}.xml"