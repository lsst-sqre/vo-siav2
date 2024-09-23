"""Validators for testing the responses of the API."""

from defusedxml import ElementTree as DefusedET
from httpx import Response


def validate_response(
    response: Response, status_code: int, content_type: str
) -> None:
    """Validate that the response is an error with the expected status code
    and content_type.

    Parameters
    ----------
    response
        The response to validate.
    status_code
        The expected status code.
    content_type
        The expected error message.

    Raises
    ------
    AssertionError
        If the response is not an expected error
    """
    assert response.status_code == status_code
    assert content_type in response.headers["Content-Type"]


def validate_votable_error(
    response: Response,
    expected_message: str | None,
) -> None:
    """Validate that the response is a VOTable error with the expected message.

    Parameters
    ----------
    response
        The response to validate.
    expected_message
        The expected error message.

    Raises
    ------
    AssertionError
        If the response is not a VOTable error with the expected message.
    """
    root = DefusedET.fromstring(response.text)
    assert root.tag == "{http://www.ivoa.net/xml/VOTable/v1.3}VOTABLE"
    assert root.attrib["version"] == "1.3"
    resource = root.find("{http://www.ivoa.net/xml/VOTable/v1.3}RESOURCE")
    assert resource is not None
    info = resource.find("{http://www.ivoa.net/xml/VOTable/v1.3}INFO")
    assert info is not None
    assert info.attrib["name"] == "QUERY_STATUS"
    assert info.attrib["value"] == "ERROR"
    if expected_message and info.text:
        assert info.text.startswith(expected_message)
