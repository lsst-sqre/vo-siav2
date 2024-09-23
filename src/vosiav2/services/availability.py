"""Service for checking the availability of the system."""

from abc import ABC, abstractmethod

from httpx import AsyncClient
from vo_models.vosi.availability import Availability

from ..config import Config
from ..exceptions import FatalFaultError
from ..models.query_engines import QueryEngines
from .config_reader import get_data_collection


class AvailabilityChecker(ABC):
    """Base class for availability checkers."""

    @abstractmethod
    async def check_availability(self, config: Config) -> Availability:
        """Check the availability of the query engine.

        Parameters
        ----------
        config
            The app configuration

        Returns
        -------
        Availability
            The availability of the query engine.
        """


class DirectButlerAvailabilityChecker(AvailabilityChecker):
    """Checker for the availability of the direct Butler query engine."""

    async def check_availability(self, config: Config) -> Availability:
        """Check the availability of the direct Butler query engine
        For now this just returns Available(True). We could improve this by
        checking if we can create a valid Butler with the config provided.

        Parameters
        ----------
        config
            The app configuration

        Returns
        -------
        Availability
            The availability of the direct Butler query engine.
        """
        return Availability(available=True)


class RemoteButlerAvailabilityChecker(AvailabilityChecker):
    """Checker for the availability of the remote Butler query engine."""

    async def check_availability(self, config: Config) -> Availability:
        """Check the availability of the remote Butler query engine
        This checks if the remote Butler is available by sending a GET request
        to the root URL of the remote Butler.

        Parameters
        ----------
        config
            The app configuration

        Returns
        -------
        Availability
            The availability of the remote Butler query engine.
        """
        async with AsyncClient() as client:
            try:
                default_collection = get_data_collection(
                    label=config.default_collection_label, config=config
                )

                repository = default_collection.repository
                r = await client.get(repository) if repository else None
                if not r:
                    return Availability(available=False)

                return Availability(available=r.status_code == 200)

            except (KeyError, ValueError, FatalFaultError):
                return Availability(available=False)


class AvailabilityService:
    """Service for checking the availability of the system."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.checkers: dict[QueryEngines, AvailabilityChecker] = {
            QueryEngines.DIRECT_BUTLER: DirectButlerAvailabilityChecker(),
            QueryEngines.REMOTE_BUTLER: RemoteButlerAvailabilityChecker(),
        }

    async def get_availability(self) -> Availability:
        """Check the availability of the system.

        Returns
        -------
        Availability
            The availability of the query engine.
        """
        checker = self.checkers.get(self.config.query_engine)
        if checker:
            return await checker.check_availability(config=self.config)
        else:
            return Availability(available=True)
