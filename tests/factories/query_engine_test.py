"""Tests for the QueryEngineFactory class."""

from unittest.mock import Mock

import pytest

from vosiav2.config import Config
from vosiav2.exceptions import FatalFaultError
from vosiav2.factories.query_engine_factory import QueryEngineFactory
from vosiav2.models.query_engines import QueryEngines
from vosiav2.services.butler_query_engine import RemoteButlerQueryEngine


@pytest.fixture
def mock_config() -> Config:
    """Return a mock Config instance."""
    return Config()


@pytest.fixture
def query_engine_factory(mock_config: Config) -> QueryEngineFactory:
    """Return a QueryEngineFactory instance."""
    return QueryEngineFactory(mock_config)


@pytest.fixture
def mock_labeled_butler_factory(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Return a mock LabeledButlerFactory instance."""
    mock = Mock()
    monkeypatch.setattr(
        "vosiav2.factories.query_engine_factory.LabeledButlerFactory", mock
    )
    return mock


@pytest.fixture
def mock_butler_config(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Return a mock ButlerConfig instance."""
    mock = Mock()
    monkeypatch.setattr(
        "vosiav2.factories.query_engine_factory.ButlerConfig", mock
    )
    return mock


@pytest.fixture
def mock_exporter_config(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Return a mock ExporterConfig instance."""
    mock = Mock()
    monkeypatch.setattr(
        "vosiav2.factories.query_engine_factory.ExporterConfig", mock
    )
    return mock


def test_create_remote_butler_success(
    query_engine_factory: QueryEngineFactory,
    mock_labeled_butler_factory: Mock,
    mock_butler_config: Mock,
    mock_exporter_config: Mock,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance."""
    mock_butler = Mock()
    mock_labeled_butler_factory.return_value.create_butler.return_value = (
        mock_butler
    )
    mock_exporter_config.model_validate.return_value = Mock()

    result = query_engine_factory._create_remote_butler(
        token="test_token", label="test_label", config="test_config"
    )

    assert isinstance(result, RemoteButlerQueryEngine)
    mock_labeled_butler_factory.assert_called_once()
    mock_butler_config.assert_called_once_with("test_config")
    mock_exporter_config.model_validate.assert_called_once()


def test_create_remote_butler_missing_label(
    query_engine_factory: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with missing label."""
    with pytest.raises(FatalFaultError, match="No Butler label configured"):
        query_engine_factory._create_remote_butler(
            token="test_token", config="test_config"
        )


def test_create_remote_butler_missing_token(
    query_engine_factory: QueryEngineFactory,
) -> None:
    """Test creating a RemoteButlerQueryEngine instance with missing token."""
    with pytest.raises(FatalFaultError, match="Token is required"):
        query_engine_factory._create_remote_butler(
            label="test_label", config="test_config"
        )


def test_create_remote_butler_missing_config(
    query_engine_factory: QueryEngineFactory,
) -> None:
    with pytest.raises(
        FatalFaultError, match="No Butler configuration file configured"
    ):
        query_engine_factory._create_remote_butler(
            token="test_token", label="test_label"
        )


def test_engine_creators_mapping(
    query_engine_factory: QueryEngineFactory,
) -> None:
    assert QueryEngines.REMOTE_BUTLER in query_engine_factory.engine_creators
    assert callable(
        query_engine_factory.engine_creators[QueryEngines.REMOTE_BUTLER]
    )
