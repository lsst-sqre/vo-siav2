"""Config reader helper methods."""

from ..config import Config
from ..config import config as app_config
from ..exceptions import FatalFaultError, UsageFaultError
from ..models.data_collections import DataCollection


def get_data_collection(label: str | None, config: Config) -> DataCollection:
    """Return the Data collection URL for the given label.
    If no label is provided, return the default data collection.

    Parameters
    ----------
    label
        The label of the data collection.
    config
        The configuration dictionary.

    Returns
    -------
    DataCollection
        The Data collection.

    Raises
    ------
    KeyError
        If the label is not found in the Data collections.
    """
    if not label:
        if len(config.data_collections) == 0:
            raise FatalFaultError(
                detail="No Data Collections configured. Please configure at "
                "least one Data collection."
            )
        # Return the first one if no label is provided
        return config.data_collections[0]

    # Find the Data collection with the given label
    # Do a case-sensitive search
    for collection in config.data_collections:
        if collection.label == label:
            return collection

    raise UsageFaultError(
        detail="Label {label} not found in Data collections."
    )


def get_data_repositories(config: Config) -> dict[str, str]:
    """Read the Data repositories from config and return a dictionary
    mapping labels to repository URLs.

    Returns
    -------
    dict
        A dictionary mapping labels to repository URLs.
    """
    butler_repos = {}

    for collection in config.data_collections:
        label = collection.label
        repository = collection.repository

        if label and repository:
            butler_repos[label] = repository

    return butler_repos


data_repositories = get_data_repositories(config=app_config)
"""A dictionary mapping labels to repository URLs."""
