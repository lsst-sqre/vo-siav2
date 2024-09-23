"""Support module for mockign a Butler."""

from unittest.mock import Mock

import astropy


class MockButlerEngine:
    def __init__(self) -> None:
        self.siav2_query = Mock()
        self.siav2_query.return_value = self.create_obscore_votable()

    @staticmethod
    def create_obscore_votable() -> astropy.io.votable.tree.VOTableFile:
        """Create a mock ObsCore VOTable.

        Returns
        -------
        astropy.io.votable.tree.VOTableFile
            The mock ObsCore VOTable.
        """
        from astropy.io.votable import from_table
        from astropy.table import Table

        # Create an Astropy Table with Obscore columns
        t = Table(
            names=(
                "dataproduct_type",
                "s_ra",
                "s_dec",
                "s_fov",
                "t_min",
                "t_max",
                "em_min",
                "em_max",
                "o_ucd",
                "access_url",
                "access_format",
                "obs_publisher_did",
            ),
            dtype=(
                "str",
                "float",
                "float",
                "float",
                "str",
                "str",
                "float",
                "float",
                "str",
                "str",
                "str",
                "str",
            ),
        )

        t.add_row(
            (
                "image",
                180.0,
                -30.0,
                0.1,
                "2020-01-01",
                "2020-01-02",
                4.0e-7,
                7.0e-7,
                "phot.flux",
                "http://example.com/image.fits",
                "application/fits",
                "ivo://example/123",
            )
        )

        return from_table(t)
