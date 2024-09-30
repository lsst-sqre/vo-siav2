"""Tests for the config_reader module."""

from unittest.mock import Mock

import pytest

from vosiav2.config import Config
from vosiav2.exceptions import FatalFaultError, UsageFaultError
from vosiav2.factories.query_engine_factory import QueryEngineFactory
from vosiav2.models.data_collections import DataCollection
from vosiav2.models.query_engines import QueryEngines
from vosiav2.services.config_reader import (
    get_data_collection,
    get_data_repositories,
)


@pytest.fixture
def test_config_invalid() -> Config:
    """Return a test configuration with an invalid Data Collection."""
    butler_collections = [
        DataCollection(
            config="invalid_config.yaml",
            repository="invalid_repo",
            default=False,
        ),
    ]
    return Config(
        query_engine=QueryEngines.REMOTE_BUTLER,
        data_collections=butler_collections,
    )


@pytest.fixture
def query_engine_factory_remote(
    test_config_remote: Config,
) -> QueryEngineFactory:
    """Return a QueryEngineFactory instance for a remote Butler engine."""
    return QueryEngineFactory(test_config_remote)


@pytest.fixture
def query_engine_factory_direct(
    test_config_direct: Config,
) -> QueryEngineFactory:
    """Return a QueryEngineFactory instance for a direct Butler engine."""
    return QueryEngineFactory(test_config_direct)


@pytest.fixture
def query_engine_factory_invalid(
    test_config_invalid: Config,
) -> QueryEngineFactory:
    """Return a QueryEngineFactory instance with an invalid Data Collection."""
    return QueryEngineFactory(test_config_invalid)


@pytest.fixture
def mock_remote_butler_query_engine(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Return a mock RemoteButlerQueryEngine instance."""
    mock = Mock()
    monkeypatch.setattr(
        "vosiav2.factories.query_engine_factory.RemoteButlerQueryEngine", mock
    )
    return mock


@pytest.fixture
def empty_config() -> Config:
    """Return a test configuration with no Data Collections."""
    return Config(
        query_engine=QueryEngines.REMOTE_BUTLER,
        data_collections=[],
    )


@pytest.mark.asyncio
async def test_get_data_repositories(test_config_remote: Config) -> None:
    """Test get_data_repositories function."""
    expected_repos = {
        "LSST.DP02": "https://data-dev.lsst.cloud/api/butler/repo/dp02/butler.yaml"
    }

    result = get_data_repositories(test_config_remote)

    assert (
        result == expected_repos
    ), f"Expected {expected_repos}, but got {result}"
    assert len(result) == 1, f"Expected 1 repository, but got {len(result)}"
    assert "LSST.DP02" in result, "Expected 'LSST.DP02' to be in the result"
    assert (
        result["LSST.DP02"]
        == "https://data-dev.lsst.cloud/api/butler/repo/dp02/butler.yaml"
    ), f"Unexpected repository URL for LSST.DP02: {result['LSST.DP02']}"


@pytest.mark.asyncio
async def test_get_data_collection_with_label(
    test_config_remote: Config,
) -> None:
    """Test get_data_collection function with a label."""
    label = "LSST.DP02"
    result = get_data_collection(label, test_config_remote)
    assert result.label == label
    assert (
        result.repository
        == "https://data-dev.lsst.cloud/api/butler/repo/dp02/butler.yaml"
    )


@pytest.mark.asyncio
async def test_get_data_collection_no_label(
    test_config_remote: Config,
) -> None:
    """Test get_data_collection function with no label."""
    result = get_data_collection(None, test_config_remote)
    assert result.label == "LSST.DP02"
    assert (
        result.repository
        == "https://data-dev.lsst.cloud/api/butler/repo/dp02/butler.yaml"
    )


@pytest.mark.asyncio
async def test_get_data_collection_empty_config(empty_config: Config) -> None:
    """Test get_data_collection function with an empty configuration."""
    with pytest.raises(
        FatalFaultError, match="No Data Collections configured"
    ):
        get_data_collection(None, empty_config)


@pytest.mark.asyncio
async def test_get_data_collection_invalid_label(
    test_config_remote: Config,
) -> None:
    """Test get_data_collection function with an invalid label."""
    with pytest.raises(
        UsageFaultError,
        match="Label InvalidLabel not found in Data collections",
    ):
        get_data_collection("InvalidLabel", test_config_remote)


@pytest.mark.asyncio
async def test_get_data_collection_case_sensitive(
    test_config_remote: Config,
) -> None:
    """Test get_data_collection function with a case-sensitive label."""
    with pytest.raises(
        UsageFaultError, match="Label lsst.dp02 not found in Data collections"
    ):
        get_data_collection("lsst.dp02", test_config_remote)


def test_create_remote_butler_missing_label(
    query_engine_factory_remote: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with missing label."""
    with pytest.raises(FatalFaultError, match="No Butler label configured"):
        query_engine_factory_remote._create_remote_butler(
            token="test_token", config="test_config"
        )


def test_create_remote_butler_missing_token(
    query_engine_factory_remote: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with missing token."""
    with pytest.raises(FatalFaultError, match="Token is required"):
        query_engine_factory_remote._create_remote_butler(
            label="LSST.DP02", config="test_config"
        )


def test_create_remote_butler_missing_config(
    query_engine_factory_remote: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with missing config."""
    with pytest.raises(
        FatalFaultError, match="No Butler configuration file configured"
    ):
        query_engine_factory_remote._create_remote_butler(
            token="test_token", label="LSST.DP02"
        )


def test_engine_creators_mapping_remote(
    query_engine_factory_remote: QueryEngineFactory,
) -> None:
    """Test the engine_creators mapping for a remote Butler engine."""
    assert (
        QueryEngines.REMOTE_BUTLER
        in query_engine_factory_remote.engine_creators
    )
    assert callable(
        query_engine_factory_remote.engine_creators[QueryEngines.REMOTE_BUTLER]
    )


def test_engine_creators_mapping_direct(
    query_engine_factory_direct: QueryEngineFactory,
) -> None:
    """Test the engine_creators mapping for a direct Butler engine."""
    assert (
        QueryEngines.DIRECT_BUTLER
        in query_engine_factory_direct.engine_creators
    )
    assert callable(
        query_engine_factory_direct.engine_creators[QueryEngines.DIRECT_BUTLER]
    )


def test_invalid_config(
    query_engine_factory_invalid: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with an
    invalid config.
    """
    with pytest.raises(KeyError):
        query_engine_factory_invalid._create_remote_butler(
            token="test_token", label="invalid", config="invalid_config.yaml"
        )
