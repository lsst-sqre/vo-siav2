"""SIAv2 query parameters models."""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Annotated, Any

from fastapi import Query

from ..models.common import CaseInsensitiveEnum

__all__ = [
    "BaseQueryParams",
    "SIAv2QueryParams",
    "Shape",
    "DPType",
    "Polarization",
    "CalibLevel",
]


class CalibLevel(int, Enum):
    """Enumeration of possible calibration levels."""

    LEVEL0 = 0
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3


class Shape(CaseInsensitiveEnum):
    """Enumeration of possible shapes for the POS parameter."""

    CIRCLE = "CIRCLE"
    RANGE = "RANGE"
    POLYGON = "POLYGON"


class DPType(CaseInsensitiveEnum):
    """Enumeration of possible data product types."""

    IMAGE = "IMAGE"
    CUBE = "CUBE"


class Polarization(CaseInsensitiveEnum):
    """Enumeration of possible polarization states."""

    I = "I"  # noqa: E741
    Q = "Q"
    U = "U"
    V = "V"
    RR = "RR"
    LL = "LL"
    RL = "RL"
    LR = "LR"
    XX = "XX"
    YY = "YY"
    XY = "XY"
    YX = "YX"


class BaseQueryParams(ABC):
    """Base class for query parameters."""

    @abstractmethod
    def to_engine_parameters(self) -> Any:
        """Convert the query parameters to the format expected by the
        specific query engine.
        """


@dataclass
class SIAv2QueryParams:
    """A class to represent the parameters for an SIAv2 query.

    Attributes
    ----------
    pos : Optional[list[str]]
        Positional region(s) to be searched.
    q_format : Optional[list[str]]
        Image format(s).
    time : Optional[list[str]]
        Time interval(s) to be searched.
    band : Optional[list[str]]
        Band interval(s) to be searched.
    pol : Optional[list[Polarization]]
        Polarization state(s) to be searched.
    fov : Optional[list[str]]
        Range(s) of field of view.
    spatres : Optional[list[str]]
        Range(s) of spatial resolution.
    exptime : Optional[list[str]]
        Range(s) of exposure times.
    timeres : Optional[list[str]]
        Range(s) of temporal resolution.
    specrp : Optional[list[str]]
        Range(s) of spectral resolving power.
    q_id : Optional[list[str]]
        Identifier of dataset(s). (Case insensitive)
    dptype : Optional[list[DPType]]
        Type of data (dataproduct_type).
    calib : Optional[list[CalibLevel]]
        Calibration level of the data.
    target : Optional[list[str]]
        Name of the target.
    collection : Optional[list[str]]
        Name of the data collection.
    facility : Optional[list[str]]
        Name of the facility.
    instrument : Optional[list[str]]
        Name of the instrument.
    maxrec : Optional[int]
        Maximum number of records in the response.
    responseformat : Optional[str]
        Format of the response.
    """

    pos: Annotated[
        list[str] | None,
        Query(
            title="pos",
            description="Positional region(s) to be searched",
            examples=["320 -0.1 10"],
        ),
    ] = None

    q_format: Annotated[
        list[str] | None,
        Query(
            title="format",
            alias="format",
            description="Response format(s)",
            examples=["application/x-votable+xml"],
        ),
    ] = None

    time: Annotated[
        list[str] | None,
        Query(
            title="time",
            description="Time interval(s) to be searched",
            examples=["2021-01-01T00:00:00Z 2021-01-02T00:00:00Z"],
        ),
    ] = None

    band: Annotated[
        list[str] | None,
        Query(
            title="band",
            description="Energy interval(s) to be searched",
            examples=["0.1 10.0"],
        ),
    ] = None

    pol: Annotated[
        list[Polarization] | None,
        Query(
            title="pol",
            description="Polarization state(s) to be searched",
            examples=["I", "Q"],
        ),
    ] = None

    fov: Annotated[
        list[str] | None,
        Query(
            title="fov",
            description="Range(s) of field of view",
            examples=["1.0 2.0"],
        ),
    ] = None

    spatres: Annotated[
        list[str] | None,
        Query(
            title="spatres",
            description="Range(s) of spatial resolution",
            examples=["0.1 0.2"],
        ),
    ] = None

    exptime: Annotated[
        list[str] | None,
        Query(
            title="exptime",
            description="Range(s) of exposure times",
            examples=["-Inf 60"],
        ),
    ] = None

    timeres: Annotated[
        list[str] | None,
        Query(
            title="timeres",
            description="Range(s) of temporal resolution",
            examples=["-Inf 1.0"],
        ),
    ] = None

    specrp: Annotated[
        list[str] | None,
        Query(
            title="specrp",
            description="Range(s) of spectral resolving power",
            examples=["1000 2000"],
        ),
    ] = None

    q_id: Annotated[
        list[str] | None,
        Query(
            title="id",
            alias="id",
            description="Identifier of dataset(s)",
            examples=["obs_id_1"],
        ),
    ] = None

    dptype: Annotated[
        list[DPType] | None,
        Query(title="dptype", description="Type of data", examples=["image"]),
    ] = None

    calib: Annotated[
        list[CalibLevel] | None,
        Query(
            title="calib",
            description="Calibration level of the data",
            examples=[0, 1, 2],
        ),
    ] = None

    target: Annotated[
        list[str] | None,
        Query(
            title="target", description="Name of the target", examples=["M31"]
        ),
    ] = None

    collection: Annotated[
        list[str] | None,
        Query(
            title="collection",
            description="Name of the data collection",
            examples=["HST"],
        ),
    ] = None

    facility: Annotated[
        list[str] | None,
        Query(
            title="facility",
            description="Name of the facility",
            examples=["HST"],
        ),
    ] = None

    instrument: Annotated[
        list[str] | None,
        Query(
            title="instrument",
            description="Name of the instrument",
            examples=["ACS"],
        ),
    ] = None

    maxrec: Annotated[
        int | None,
        Query(
            title="maxrec",
            description="Maximum number of records in the response",
            examples=[10],
        ),
    ] = None

    responseformat: Annotated[
        str | None,
        Query(
            title="reponseformat",
            description="Format of the response",
            examples=["application/x-votable+xml"],
        ),
    ] = None

    def to_engine_parameters(self) -> dict[str, Any]:
        """Convert the query parameters to a dictionary. Exclude None
        values.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}
