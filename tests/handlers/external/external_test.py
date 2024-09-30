"""Tests for the vosiav2.handlers.external module and routes."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

from tests.support.butler import MockButlerEngine
from tests.support.constants import EXCEPTION_MESSAGES
from tests.support.validators import validate_votable_error
from vosiav2.config import config
from vosiav2.constants import RESULT_NAME


@pytest.mark.asyncio
async def test_get_index(client: AsyncClient) -> None:
    """Test ``GET /api/sia/``."""
    response = await client.get(f"{config.path_prefix}/")
    assert response.status_code == 200
    data = response.json()
    metadata = data["metadata"]
    assert metadata["name"] == config.name
    assert isinstance(metadata["version"], str)
    assert isinstance(metadata["description"], str)
    assert isinstance(metadata["repository_url"], str)
    assert isinstance(metadata["documentation_url"], str)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "query_params",
        "expected_status",
        "expected_content_type",
        "expected_message",
    ),
    [
        (
            "POS=CIRCLE+320+-0.1+10.7",
            200,
            "application/x-votable+xml",
            None,
        ),
        (
            "POS=CIRCLE+320+-0.1+10.7&TIME=-Inf++Inf",
            200,
            "application/x-votable+xml",
            None,
        ),
        (
            "POS=CIRCLE+320+-0.1+10.7&TIME=-Inf++Inf&DP_TYPE=image",
            200,
            "application/x-votable+xml",
            None,
        ),
        (
            "pos=CIRCLE+320+-0.1+10.7&TIME=-Inf++Inf&DP_TYPE=image",
            200,
            "application/x-votable+xml",
            None,
        ),
        (
            "POS=RANGE+0+360.0+-2.0+2.0&TIME=-Inf++Inf&DP_TYPE=image&dp_type"
            "=cube",
            200,
            "application/x-votable+xml",
            None,
        ),
    ],
)
async def test_query_endpoint_mocker_get(
    client: AsyncClient,
    query_params: str,
    expected_status: int,
    expected_content_type: str,
    expected_message: str | None,
    mock_query_engine: MockButlerEngine,
    expected_votable: str,
) -> None:
    """Test ``GET /api/sia/query`` with valid parameters but use a Mocker
    for the query engine.
    """
    response = await client.get(
        f"{config.path_prefix}/query?{query_params}",
    )
    assert response.text == expected_votable
    assert response.status_code == expected_status
    assert response.headers["content-type"] == expected_content_type
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"].startswith(
        f"attachment; filename={RESULT_NAME}.xml",
    )
    mock_query_engine.siav2_query.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "query_params",
        "expected_status",
        "expected_content_type",
        "expected_message",
    ),
    [
        (
            "POS=SOME_SHAPE+321+0+1&BAND=700e-9&FORMAT=votable",
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_pos"],
        ),
        (
            "POS=CIRCLE+0+0+1&TIME=ABC",
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_time"],
        ),
        (
            "POS=CIRCLE+0+0+1&CALIB=6",
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_calib"],
        ),
        (
            "MAXREC=0",
            200,
            "application/x-votable+xml",
            None,
        ),
    ],
)
async def test_query_endpoint_get(
    client: AsyncClient,
    query_params: str,
    expected_status: int,
    expected_content_type: str,
    expected_message: str | None,
    mock_query_engine: MockButlerEngine,
) -> None:
    """Test ``GET /api/sia/query`` with various parameters."""
    response = await client.get(f"{config.path_prefix}/query?{query_params}")

    assert response.status_code == expected_status
    assert expected_content_type in response.headers["content-type"]

    if expected_status == 200:
        assert "content-disposition" in response.headers
        assert response.headers["content-disposition"].startswith(
            f"attachment; filename={RESULT_NAME}.xml"
        )
    elif expected_status == 400:
        validate_votable_error(response, expected_message)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "post_data",
        "expected_status",
        "expected_content_type",
        "expected_message",
    ),
    [
        (
            {
                "POS": "SOME_SHAPE 321 0 1",
                "BAND": "700e-9",
                "FORMAT": "votable",
            },
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_pos"],
        ),
        (
            {"POS": "CIRCLE 0 0 1", "TIME": "ABC"},
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_time"],
        ),
        (
            {"POS": "CIRCLE 0 0 1", "CALIB": "6"},
            400,
            "application/xml",
            EXCEPTION_MESSAGES["invalid_calib"],
        ),
        (
            {"MAXREC": "0"},
            200,
            "application/x-votable+xml",
            None,
        ),
    ],
)
async def test_query_endpoint_post(
    client: AsyncClient,
    post_data: dict[str, Any],
    expected_status: int,
    expected_content_type: str,
    expected_message: str | None,
    mock_query_engine: MockButlerEngine,
) -> None:
    """Test ``POST /api/sia/query`` with various parameters."""
    response = await client.post(f"{config.path_prefix}/query", data=post_data)

    assert response.status_code == expected_status
    assert expected_content_type in response.headers["content-type"]

    if expected_status == 200:
        assert "content-disposition" in response.headers
        assert response.headers["content-disposition"].startswith(
            f"attachment; filename={RESULT_NAME}.xml"
        )
    elif expected_status == 400:
        validate_votable_error(response, expected_message)
