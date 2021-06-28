import doctest
from plone.testing import layered
import unittest2 as unittest
from transmogrify.dexterity.testing import TRANSMOGRIFY_DEXTERITY_INTEGRATION_TESTING  # noqa

OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


TESTFILES = (
    'schemaupdater.txt',
    'pipelinescsvsource.txt',
)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                filename,
                optionflags=OPTIONFLAGS
            ),
            layer=TRANSMOGRIFY_DEXTERITY_INTEGRATION_TESTING
        )
        for filename in TESTFILES
    ])
    return suite
