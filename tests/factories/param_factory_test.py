"""Test the ParamFactory class."""

from typing import Any

import pytest
from lsst.dax.obscore.siav2 import SIAv2Parameters

from sia.config import Config
from sia.factories.param_factory import ParamFactory
from sia.models.query_engines import QueryEngines
from sia.models.sia_query_params import (
    CalibLevel,
    DPType,
    Polarization,
    SIAQueryParams,
)


@pytest.fixture
def sia_params() -> SIAQueryParams:
    """Return a SIAQueryParams instance."""
    return SIAQueryParams(
        pos=["CIRCLE 0 1 1"],
        q_format=["application/fits"],
        time=["55 55"],
        band=["0.1 10.0"],
        pol=[Polarization("I"), Polarization("Q")],
        fov=["1.0 2.0"],
        spatres=["0.1 0.2"],
        exptime=["-Inf 60"],
        timeres=["-Inf 1.0"],
        specrp=["1000 2000"],
        q_id=["obs_id_1"],
        dptype=[DPType("image")],
        calib=[CalibLevel(0), CalibLevel(1), CalibLevel(2)],
        target=["M31"],
        collection=["HST"],
        facility=["HST"],
        instrument=["ACS"],
        maxrec=10,
        responseformat="application/x-votable+xml",
    )


@pytest.mark.parametrize(
    ("engine", "expected_type"),
    [
        (QueryEngines.DIRECT_BUTLER, SIAv2Parameters),
        (QueryEngines.REMOTE_BUTLER, SIAv2Parameters),
    ],
)
def test_param_factory(
    engine: QueryEngines, expected_type: Any, sia_params: SIAQueryParams
) -> None:
    """Test the ParamFactory class."""
    config = Config(query_engine=engine)
    factory = ParamFactory(config)
    adapter = factory.create_params(sia_params)
    engine_specific_params = adapter.to_engine_parameters()
    assert isinstance(engine_specific_params, expected_type)
