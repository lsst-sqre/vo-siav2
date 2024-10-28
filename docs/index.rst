.. toctree::
   :maxdepth: 1
   :hidden:

   usage/index
   admin/index
   api

###########
SIA
###########
SIA is an implementation of the IVOA `Simple Image Access v2`_ protocol as a `FastAPI`_ web service, designed to be deployed as part of the Rubin Science Platform through `Phalanx`_.
It provides a capability of discovering, retrieving and gathering metadata for image holdings, via the use of the ObsCore Data Model.
Users will in most cases be accessing the service via other client tools like **Firefly** or **TopCat** which abstract the data access flow behind user-friendly interfaces.

The default configuration uses the `dax_obscore`_ package and interacts with a `Butler`_ repository to find images matching specific criteria. While the current release supports both remote and direct (local) Butler repositories, our primary focus has been on the Remote Butler use-case, resulting in more mature support for this option.
The application expects as part of the configuration a list of Butler Data Collections, each of which expects a number of attributes which define how to access the repository.

The github repository for `SIA`_ is where the application is developed. See the `CHANGELOG`_ for a list of versions and changes to the application.

The system architecture & design considerations have been documented in https://github.com/lsst-sqre/sqr-095.

.. grid:: 1

   .. grid-item-card:: Usage
      :link: usage/index
      :link-type: doc

      Learn how to use the SIAv2 Service.

   .. grid-item-card:: Admin
      :link: admin/index
      :link-type: doc

      Learn how to setup the application.

.. _Simple Image Access v2: https://www.ivoa.net/documents/SIA/
.. _FastAPI: https://fastapi.tiangolo.com/
.. _Phalanx: https://github.com/lsst-sqre/phalanx
.. _dax_obscore: https://github.com/lsst-dm/dax_obscore
.. _Butler: https://github.com/lsst/daf_butler
.. _SIA: https://github.com/lsst-sqre/sia
.. _CHANGELOG: https://github.com/lsst-sqre/sia/blob/main/CHANGELOG.md
