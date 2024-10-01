"""Constants for the SIA service."""

__all__ = [
    "RESPONSEFORMATS",
    "COLLECTIONS",
    "RESULT_NAME",
    "SINGLE_PARAMS",
]

from .models.data_collections import DataCollection

RESPONSEFORMATS = {"votable", "application/x-votable"}
"""List of supported response formats for the SIA service."""

RESULT_NAME = "result"
"""The name of the result file."""

COLLECTIONS = [
    DataCollection(
        config="https://raw.githubusercontent.com/lsst-dm/dax_obscore"
        "/253b157fccdb8d9255bb4afbe9bf729618cdb367/configs/dp02.yaml",
        label="LSST.DP02",
        repository=(
            "https://data-dev.lsst.cloud/api/butler/repo/dp02/butler.yaml"
        ),
        default=True,
    ),
]
"""Configuration for a query engine."""


SINGLE_PARAMS = {
    "maxrec",
    "responseformat",
}
"""Parameters that should be treated as single values."""
