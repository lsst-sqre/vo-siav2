"""A Butler Query Engine service, used  for performing an SIA query via the
use of Butler.
"""

from dataclasses import dataclass

import astropy
from lsst.daf.butler import Butler
from lsst.dax.obscore import ExporterConfig
from lsst.dax.obscore.siav2 import SIAv2Parameters
from lsst.dax.obscore.siav2 import siav2_query as butler_siav2_query

from ..services.base_query_engine import SIABaseQueryEngine

__all__ = [
    "BaseButlerQueryEngine",
    "RemoteButlerQueryEngine",
    "DirectButlerQueryEngine",
]


@dataclass
class BaseButlerQueryEngine(SIABaseQueryEngine):
    """A service for performing a SIAv2 query via the use of Butler."""

    butler: Butler
    config: ExporterConfig

    def sia_query(
        self, params: SIAv2Parameters
    ) -> astropy.io.votable.tree.VOTableFile:
        """Perform a SIAv2 query.

        Parameters
        ----------
        params
            SIAv2Parameters object containing the parameters for the query.

        Returns
        -------
        astropy.io.votable.tree.VOTableFile
            The VOTable file containing the results of the query
        """
        return butler_siav2_query(
            butler=self.butler, config=self.config, parameters=params
        )


@dataclass
class RemoteButlerQueryEngine(BaseButlerQueryEngine):
    """Implementation of the Butler Query Engine that uses a Remote
    Butler to run the SIAv2 Query.
    """

    label: str
    token: str


@dataclass
class DirectButlerQueryEngine(BaseButlerQueryEngine):
    """Implementation of the Butler Query Engine that uses a Direct (Local)
    Butler to run the SIAv2 Query.
    """

    repo: str
