"""Provides functions to get instances of QueryEngineFactory and
ParamFactory.
"""

from ..config import config
from ..factories.param_factory import ParamFactory
from ..factories.query_engine_factory import QueryEngineFactory


def get_query_engine_factory() -> QueryEngineFactory:
    """Return a QueryEngineFactory instance."""
    return QueryEngineFactory(config)


def get_param_factory() -> ParamFactory:
    """Return a ParamFactory instance."""
    return ParamFactory(config)
