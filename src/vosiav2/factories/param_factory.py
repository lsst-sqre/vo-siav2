"""FastAPI dependencies for the SIAV2 service."""

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from numbers import Integral
from typing import Any, TypeVar, cast

from lsst.dax.obscore.siav2 import SIAv2Parameters

from ..config import Config
from ..models import SIAv2QueryParams
from ..models.query_engines import QueryEngines
from ..models.siav2_query_params import BaseQueryParams, CalibLevel

__all__ = ["ParamFactory"]


class SIAv2QueryParamsAdapter(BaseQueryParams):
    """Adapter class for converting SIAv2QueryParams to a dictionary.

    Parameters
    ----------
    siav2_params : SIAv2QueryParams
        The SIAv2QueryParams instance to be converted.
    """

    def __init__(self, siav2_params: SIAv2QueryParams) -> None:
        self.siav2_params = siav2_params

    def to_engine_parameters(self) -> dict[str, Any]:
        """
        Convert the SIAv2QueryParams to a dictionary.
        Method can be overridden in subclasses if a different format is needed.

        Returns
        -------
        Dict[str, Any]
            The query parameters as a dictionary.
        """
        return {
            k: v for k, v in asdict(self.siav2_params).items() if v is not None
        }


T = TypeVar("T", bound=int | str | float)


@dataclass
class ButlerQueryParamsAdapter(BaseQueryParams):
    siav2_params: SIAv2QueryParams

    def to_engine_parameters(self) -> SIAv2Parameters:
        return SIAv2Parameters.from_siav2(
            instrument=self.siav2_params.instrument or (),
            pos=self.siav2_params.pos or (),
            time=self.siav2_params.time or (),
            band=self.siav2_params.band or (),
            exptime=self.siav2_params.exptime or (),
            calib=self._convert_calib(self.siav2_params.calib),
        )

    def _convert_calib(
        self, calib: list[CalibLevel] | None
    ) -> Iterable[Integral]:
        if calib is None:
            return ()
        return cast(list[Integral], [int(level.value) for level in calib])


class ParamFactory:
    """Factory class for creating query parameter instances.

    Parameters
    ----------
    config : Config
        The configuration dictionary.

    Attributes
    ----------
    config : Config
        The configuration dictionary.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def create_params(self, siav2_params: SIAv2QueryParams) -> BaseQueryParams:
        if self.config.query_engine in (
            QueryEngines.DIRECT_BUTLER,
            QueryEngines.REMOTE_BUTLER,
        ):
            return ButlerQueryParamsAdapter(siav2_params)
        else:
            return SIAv2QueryParamsAdapter(siav2_params)
