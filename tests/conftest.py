"""Test fixtures for sia tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from sia import main
from sia.config import Config
from sia.factories.query_engine_factory import QueryEngineFactory
from sia.models.data_collections import DataCollection
from sia.models.query_engines import QueryEngines

from .support.butler import MockButlerEngine


@pytest_asyncio.fixture
async def app() -> AsyncIterator[FastAPI]:
    """Return a configured test application.

    Wraps the application in a lifespan manager so that startup and shutdown
    events are sent during test execution.
    """
    async with LifespanManager(main.app):
        yield main.app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Return an ``httpx.AsyncClient`` configured to talk to the test app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://example.com/",
        headers={"X-Auth-Request-Token": "sometoken"},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def expected_votable() -> str:
    """Return the expected VOTable content as a string."""
    base_path = Path(__file__).parent
    xml_file_path = base_path / "templates" / "expected_votable.xml"
    with xml_file_path.open("r", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def mock_query_engine(monkeypatch: pytest.MonkeyPatch) -> MockButlerEngine:
    """Return a mock ButlerQueryEngine object."""
    mock_engine = MockButlerEngine()
    mock_engine.sia_query = MagicMock(
        return_value=MockButlerEngine.create_obscore_votable()
    )

    def mock_create_query_engine(
        self: QueryEngineFactory, **kwargs: Any
    ) -> MockButlerEngine:
        return mock_engine

    monkeypatch.setattr(
        QueryEngineFactory,
        "create_query_engine",
        mock_create_query_engine,
    )
    return mock_engine


@pytest_asyncio.fixture
async def test_config_remote() -> Config:
    """Return a test configuration for a remote Butler engine.

    Returns
    -------
    Config
        The test configuration
    """
    butler_collections = [
        DataCollection(
            config="https://raw.githubusercontent.com/lsst-dm/dax_obscore"
            "/253b157fccdb8d9255bb4afbe9bf729618cdb367/configs/dp02.yaml",
            label="LSST.DP02",
            repository=(
                "https://data-dev.lsst.cloud/api/butler/repo/dp02"
                "/butler.yaml"
            ),
            default=True,
        ),
    ]
    return Config(
        query_engine=QueryEngines.REMOTE_BUTLER,
        data_collections=butler_collections,
    )


@pytest_asyncio.fixture
async def test_config_direct() -> Config:
    """Return a test configuration for a direct Butler engine.

    Returns
    -------
    Config
        The test configuration
    """
    base_path = Path(__file__).parent
    repo_path = base_path / "data" / "repo"
    config_file = base_path / "data" / "config" / "ci_hsc_gen3.yaml"

    butler_collections = [
        DataCollection(
            config=str(config_file), repository=str(repo_path), default=True
        ),
    ]

    return Config(
        query_engine=QueryEngines.DIRECT_BUTLER,
        data_collections=butler_collections,
    )
