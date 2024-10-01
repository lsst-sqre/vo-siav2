"""Base class for SIAv2 query engines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

import astropy

P = TypeVar("P")


@dataclass
class SIABaseQueryEngine(ABC, Generic[P]):
    """Abstract class for query engines used to run an SIA query."""

    @abstractmethod
    def sia_query(self, params: P) -> astropy.io.votable.tree.VOTableFile:
        """Perform an SIA query.

        Parameters
        ----------
        params
            SIAv2Parameters object containing the parameters for the query.

        Returns
        -------
        astropy.io.votable.tree.VOTableFile
            The VOTable file containing the results of the query
        """
        ...
