"""Module for the Query Processor service."""

from starlette.responses import Response

from ..config import config
from ..constants import RESULT_NAME
from ..exceptions import UsageFaultError
from ..factories.param_factory import ParamFactory
from ..factories.query_engine_factory import QueryEngineFactory
from ..models.sia_query_params import SIAQueryParams
from ..services.config_reader import (
    get_data_collection,
    get_default_collection,
)
from ..services.votable import VOTableConverter


def process_query(
    params: SIAQueryParams,
    query_engine_factory: QueryEngineFactory,
    param_factory: ParamFactory,
    delegated_token: str | None,
) -> Response:
    """Process the SIAv2 query.

    Parameters
    ----------
    params
        The parameters for the SIAv2 query.
    query_engine_factory
        The Query Engine factory dependency.
    param_factory
        The Param factory dependency.
    delegated_token
        The delegated token. (Optional)

    Returns
    -------
    Response
        The response containing the query results.
    """
    # Get the Butler collection configuration.
    # If many collections are provided, for now just look at the first one.
    # This needs to be updated to handle multiple collections.
    collection = (
        get_data_collection(label=params.collection[0], config=config)
        if params.collection is not None and len(params.collection) > 0
        else get_default_collection(config=config)
    )

    # Create the query engine
    query_engine = query_engine_factory.create_query_engine(
        token=delegated_token,
        label=collection.label,
        config=collection.config,
    )

    try:
        # Get the query params in the right format
        query_params = param_factory.create_params(
            sia_params=params
        ).to_engine_parameters()
    except ValueError as exc:
        raise UsageFaultError(detail=str(exc)) from exc

    # Execute the query
    table_as_votable = query_engine.sia_query(query_params)

    # Convert the result to a string
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
