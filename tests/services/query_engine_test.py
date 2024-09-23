"""Tests for SIAv2BaseQueryEngine Engine class."""

from __future__ import annotations

from pathlib import Path

from defusedxml import ElementTree as DefusedET

from vosiav2.config import Config
from vosiav2.factories.param_factory import ParamFactory
from vosiav2.factories.query_engine_factory import QueryEngineFactory
from vosiav2.models import SIAv2QueryParams
from vosiav2.services.votable import VOTableConverter

_BUTLER_REPO_PATH = str(Path(__file__).parent.parent / "data" / "repo")
_BUTLER_CONFIG_PATH = str(Path(__file__).parent.parent / "data" / "config")


def valid_votable(xml_string: str) -> bool:
    """Check if the VOTable structure is valid and has at least one Table row.

    Parameters
    ----------
    xml_string : str
        The VOTable XML string to validate.

    Returns
    -------
    bool
        True if the XML string is a valid VOTable with some data,
        False otherwise.
    """
    try:
        root = DefusedET.fromstring(xml_string)
        resource = root.find("{http://www.ivoa.net/xml/VOTable/v1.3}RESOURCE")
        if resource is None:
            return False

        info = resource.find("{http://www.ivoa.net/xml/VOTable/v1.3}INFO")
        if info is not None:
            if (
                info is None
                or info.get("name") != "QUERY_STATUS"
                or info.get("value") != "OK"
            ):
                return False

        table = resource.find("{http://www.ivoa.net/xml/VOTable/v1.3}TABLE")

        if table is None:
            return False

        data = table.find("{http://www.ivoa.net/xml/VOTable/v1.3}DATA")
        if data is None:
            return False

        tabledata = data.find(
            "{http://www.ivoa.net/xml/VOTable/v1.3}TABLEDATA"
        )

        if tabledata is None:
            return False

        return (
            tabledata.find("{http://www.ivoa.net/xml/VOTable/v1.3}TR")
            is not None
        )

    except DefusedET.ParseError:
        return False


def test_local_direct_butler(test_config_direct: Config) -> None:
    """Test Direct butler engine using HSC Gen3 data."""
    query_params = SIAv2QueryParams(
        pos=["CIRCLE 320 -0.1 10"],
        time=["-Inf Inf"],
    )
    query_engine = QueryEngineFactory(
        config=test_config_direct
    ).create_query_engine(
        config=test_config_direct.data_collections[0].config,
        repository=test_config_direct.data_collections[0].repository,
    )

    query_params = (
        ParamFactory(config=test_config_direct)
        .create_params(siav2_params=query_params)
        .to_engine_parameters()
    )

    table_as_votable = query_engine.siav2_query(query_params)
    result = VOTableConverter(table_as_votable).to_string()
    assert valid_votable(result)
