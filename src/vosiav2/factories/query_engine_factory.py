"""FastAPI dependencies for the SIAV2 service."""

from collections.abc import Callable
from typing import Any

import structlog
from lsst.daf.butler import Butler, LabeledButlerFactory
from lsst.daf.butler import Config as ButlerConfig
from lsst.dax.obscore import ExporterConfig

from ..config import Config
from ..exceptions import FatalFaultError
from ..models.query_engines import QueryEngines
from ..services.base_query_engine import SIAv2BaseQueryEngine
from ..services.butler_query_engine import (
    DirectButlerQueryEngine,
    RemoteButlerQueryEngine,
)
from ..services.config_reader import data_repositories

__all__ = ["QueryEngineFactory"]


class QueryEngineFactory:
    """Factory class for creating query engine instances.

    Parameters
    ----------
    config
        The configuration dictionary.

    Attributes
    ----------
    config : Config
        The configuration dictionary.
    logger : structlog.BoundLogger
        The logger instance.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = structlog.get_logger("vosiav2")
        self.engine_creators: dict[
            QueryEngines, Callable[..., SIAv2BaseQueryEngine]
        ] = {
            QueryEngines.DIRECT_BUTLER: self._create_direct_butler,
            QueryEngines.REMOTE_BUTLER: self._create_remote_butler,
        }

    def create_query_engine(self, **kwargs: Any) -> SIAv2BaseQueryEngine:
        """Create a query engine instance.

        Parameters
        ----------
        kwargs
            Additional keyword arguments.

        Returns
        -------
        SIAv2BaseQueryEngine
            The query engine instance.

        Raises
        ------
        ValueError
            If the engine type is not supported.
        """
        engine_type = self.config.query_engine
        creator = self.engine_creators.get(engine_type)
        if creator is None:
            raise ValueError(f"Unsupported engine type: {engine_type}")
        return creator(**kwargs)

    def _create_direct_butler(self, **kwargs: Any) -> DirectButlerQueryEngine:
        """Create a Butler Query Engine instance for a direct Butler.

        Parameters
        ----------
        kwargs
            Additional keyword arguments.

        Returns
        -------
        DirectButlerQueryEngine
            The Direct Butler Query Engine instance.

        Raises
        ------
        ValueError
            If the Butler repository or Butler configuration file are not
            configured.

        """
        butler_repo = kwargs.get("repository")
        butler_config = kwargs.get("config")

        if not butler_repo:
            raise ValueError("No Butler repository configured <butler_repo>")
        if not butler_config:
            raise ValueError(
                "No Butler configuration file configured <butler_config>"
            )

        butler = Butler.from_config(butler_repo, writeable=False)
        config_data = ButlerConfig(butler_config)
        exporter_config = ExporterConfig.model_validate(config_data)

        self.logger.info("DirectButlerQueryEngine created successfully")

        return DirectButlerQueryEngine(
            config=exporter_config, butler=butler, repo=butler_repo
        )

    def _create_remote_butler(self, **kwargs: Any) -> RemoteButlerQueryEngine:
        """Create a Butler Query Engine instance for a remote Butler.

        Parameters
        ----------
        kwargs
            Additional keyword arguments.

        Returns
        -------
        RemoteButlerQueryEngine
            The Remote Butler Query Engine instance.

        Raises
        ------
        ValueError
            If the Butler label, delegated token, or Butler configuration file
            are not configured.
        KeyError
            If the Butler repository does not exist.
        """
        token = kwargs.get("token")
        butler_label = kwargs.get("label")
        butler_config = kwargs.get("config")

        if not butler_label:
            raise FatalFaultError(detail="No Butler label configured <label>")
        if not token:
            raise FatalFaultError(
                detail="Token is required for RemoteButlerQueryEngine"
            )
        if not butler_config:
            raise FatalFaultError(
                detail="No Butler configuration file configured "
                "<butler_config>"
            )

        butler_factory = LabeledButlerFactory(data_repositories)
        butler = butler_factory.create_butler(
            label=butler_label, access_token=token
        )

        # TODO (stvoutsin): Temporary workaround for DP02
        from lsst.daf.butler.registry import RegistryDefaults

        butler.registry.defaults = RegistryDefaults(instrument="LSSTCam-imSim")

        config_data = ButlerConfig(butler_config)
        exporter_config = ExporterConfig.model_validate(config_data)

        self.logger.info("RemoteButlerQueryEngine created successfully")

        return RemoteButlerQueryEngine(
            config=exporter_config,
            butler=butler,
            label=butler_label,
            token=token,
        )
