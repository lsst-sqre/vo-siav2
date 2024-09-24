"""Test the capabilities' endpoint.
This test checks that the capabilities endpoint returns the
expected XML response, read from the templates/capabilities.xml file.
"""

from pathlib import Path

import pytest
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

router = APIRouter()
"""FastAPI router for all external handlers."""


@pytest.mark.asyncio
async def test_capabilities(client: AsyncClient) -> None:
    """Test the capabilities endpoint."""
    template_dir = str(
        Path(__file__).resolve().parent.parent.parent / "templates"
    )
    templates_dir = Jinja2Templates(template_dir)

    context = {
        "capabilities_url": "https://example.com/vo-siav2/capabilities",
        "availability_url": "https://example.com/vo-siav2/availability",
        "query_url": "https://example.com/vo-siav2/query",
    }

    r = await client.get("/vo-siav2/capabilities")
    assert r.status_code == 200
    template_rendered = templates_dir.get_template("capabilities.xml").render(
        context
    )

    assert r.status_code == 200

    assert r.text.strip() == template_rendered.strip()
