"""FastAPI dependencies for the SIAV2 service."""

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from numbers import Integral
from typing import Any, TypeVar, cast

from lsst.dax.obscore.siav2 import SIAv2Parameters

from ..config import Config
from ..models.query_engines import QueryEngines
from ..models.sia_query_params import (
    BaseQueryParams,
    CalibLevel,
    SIAQueryParams,
)

__all__ = ["ParamFactory"]


class SIAQueryParamsAdapter(BaseQueryParams):
    """Adapter class for converting SIAQueryParams to a dictionary.

    Parameters
    ----------
    sia_params : SIAQueryParams
        The SIAQueryParams instance to be converted.
    """

    def __init__(self, sia_params: SIAQueryParams) -> None:
        self.sia_params = sia_params

    def to_engine_parameters(self) -> dict[str, Any]:
        """
        Convert the SIAQueryParams to a dictionary.
        Method can be overridden in subclasses if a different format is needed.

        Returns
        -------
        Dict[str, Any]
            The query parameters as a dictionary.
        """
        return {
            k: v for k, v in asdict(self.sia_params).items() if v is not None
        }


T = TypeVar("T", bound=int | str | float)


@dataclass
class ButlerQueryParamsAdapter(BaseQueryParams):
    sia_params: SIAQueryParams

    def to_engine_parameters(self) -> SIAv2Parameters:
        return SIAv2Parameters.from_siav2(
            instrument=self.sia_params.instrument or (),
            pos=self.sia_params.pos or (),
            time=self.sia_params.time or (),
            band=self.sia_params.band or (),
            exptime=self.sia_params.exptime or (),
            calib=self._convert_calib(self.sia_params.calib),
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

    def create_params(self, sia_params: SIAQueryParams) -> BaseQueryParams:
        if self.config.query_engine in (
            QueryEngines.DIRECT_BUTLER,
            QueryEngines.REMOTE_BUTLER,
        ):
            return ButlerQueryParamsAdapter(sia_params)
        else:
            return SIAQueryParamsAdapter(sia_params)
