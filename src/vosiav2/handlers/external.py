"""Handlers for the app's external root, ``/vo-siav2/``."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from starlette.responses import Response
from structlog.stdlib import BoundLogger
from vo_models.vosi.availability import Availability

from ..config import config
from ..constants import RESULT_NAME
from ..dependencies.availability import get_availability_dependency
from ..dependencies.query import get_param_factory, get_query_engine_factory
from ..dependencies.token import optional_auth_delegated_token_dependency
from ..exceptions import handle_exceptions
from ..factories.param_factory import ParamFactory
from ..factories.query_engine_factory import QueryEngineFactory
from ..models import Index, SIAv2QueryParams
from ..services.config_reader import get_data_collection
from ..services.timer import timer
from ..services.votable import VOTableConverter

BASE_DIR = Path(__file__).resolve().parent.parent
_TEMPLATES = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

__all__ = ["get_index", "external_router"]

external_router = APIRouter()
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Document the top-level API here. By default it only returns metadata"
        " about the application."
    ),
    response_model=Index,
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    """GET ``/vo-siav2/`` (the app's external root).

    Customize this handler to return whatever the top-level resource of your
    application should return. For example, consider listing key API URLs.
    When doing so, also change or customize the response model in
    `vosiav2.models.Index`.

    By convention, the root of the external API includes a field called
    ``metadata`` that provides the same Safir-generated metadata as the
    internal root endpoint.
    """
    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="vo-siav2",
        application_name=config.name,
    )
    return Index(metadata=metadata)


@external_router.get(
    "/availability",
    description="VOSI-availability resource for the service",
    responses={200: {"content": {"application/xml": {}}}},
    summary="IVOA service availability",
)
async def get_availability(
    request: Request,
    availability: Annotated[
        Availability, Depends(get_availability_dependency)
    ],
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Response:
    """Endpoint which provides the VOSI-availability resource, which indicates
    whether the service is currently available, returned as an XML document.

    Parameters
    ----------
    request
        The request object.
    availability
        The system availability as dependency
    logger
        The logger instance.

    Returns
    -------
    Response
        The response containing the VOSI-availability XML document.

    ## GET /vo-siav2/availability

    **Example XML Response**:
    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <availability xmlns="http://www.ivoa.net/xml/VOSIAvailability/v1.0">
        <available>true</available>
    </availability>
    ```
    """
    xml = availability.to_xml(skip_empty=True)
    logger.info("Availability requested")
    return Response(content=xml, media_type="application/xml")


@external_router.get(
    "/capabilities",
    description="VOSI-capabilities resource for the SIAv2 service.",
    responses={200: {"content": {"application/xml": {}}}},
    summary="IVOA service capabilities",
)
async def get_capabilities(
    request: Request,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Response:
    """Endpoint which provides the VOSI-capabilities resource, which lists the
    capabilities of the SIAv2 service, as an XML document (VOSI-capabilities).

    Parameters
    ----------
    request
        The request object.
    logger
        The logger instance.

    Returns
    -------
    Response
        The response containing the VOSI-capabilities XML document.

    ## GET /vo-siav2/capabilities

    **Example XML Response**:
    ```xml
    <?xml version="1.0"?>
    <capabilities
        xmlns:vosi="http://www.ivoa.net/xml/VOSICapabilities/v1.0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:vod="http://www.ivoa.net/xml/VODataService/v1.1">
       <capability standardID="ivo://ivoa.net/std/SIA#query-2.0">
         <interface xsi:type="vod:ParamHTTP" role="std" version="2.0">
             <accessURL>{{ query_url }}</accessURL>
         </interface>
       </capability>
    </capabilities>
    ```
    """
    logger.info("Capabilities requested")

    return _TEMPLATES.TemplateResponse(
        request,
        "capabilities.xml",
        {
            "request": request,
            "availability_url": request.url_for("get_availability"),
            "capabilities_url": request.url_for("get_capabilities"),
            "query_url": request.url_for("query"),
        },
        media_type="application/xml",
    )


@external_router.get(
    "/query",
    description="Query endpoint for the SIAv2 service.",
    responses={200: {"content": {"application/xml": {}}}},
    summary="IVOA SIAv2 service query",
)
@timer
@handle_exceptions
def query(
    query_engine_factory: Annotated[
        QueryEngineFactory, Depends(get_query_engine_factory)
    ],
    param_factory: Annotated[ParamFactory, Depends(get_param_factory)],
    params: Annotated[SIAv2QueryParams, Depends()],
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
    delegated_token: Annotated[
        str | None, Depends(optional_auth_delegated_token_dependency)
    ] = None,
) -> Response:
    """Endpoint used to query the SIAv2 service using various
    parameters defined in the SIAv2 spec. The response is an XML VOTable file
    that adheres the Obscore model.

    Parameters
    ----------
    param_factory
        The Param factory dependency.
    query_engine_factory
        The Query Engine factory dependency.
    delegated_token
        The delegated token. (Optional)
    params
        The parameters for the SIAv2 query.
    logger
        The logger instance.

    Returns
    -------
    Response
        The response containing the query results.

    ## GET /vo-siav2/query

    **Example Query**:
    ```
    /vo-siav2/query?POS=CIRCLE+321+0+1&BAND=700e-9&FORMAT=votable
    ```
    **Response**:
    A VOTable XML response contains a table conforming to the ObsCore standard.
    """
    logger.info("Processing SIAv2 query with params:", params=params)

    # Get the Butler collection configuration.
    # If many collections are provided, for now just look at the first one.
    # This needs to be updated to handle multiple collections.

    collection = (
        get_data_collection(label=params.collection[0], config=config)
        if params.collection is not None and len(params.collection) > 0
        else get_data_collection(
            label=config.default_collection_label, config=config
        )
    )

    # Create the query engine and execute the query.
    query_engine = query_engine_factory.create_query_engine(
        token=delegated_token, label=collection.label, config=collection.config
    )
    query_params = param_factory.create_params(
        siav2_params=params
    ).to_engine_parameters()

    table_as_votable = query_engine.siav2_query(query_params)
    result = VOTableConverter(table_as_votable).to_string()

    # For the moment only VOTable is supported, so we can hardcode the
    # media_type and the file extension.
    return Response(
        headers={
            "content-disposition": f"attachment; filename={RESULT_NAME}.xml",
            "Content-Type": "application/x-votable+xml",
        },
        content=result,
        media_type="application/x-votable+xml",
    )
