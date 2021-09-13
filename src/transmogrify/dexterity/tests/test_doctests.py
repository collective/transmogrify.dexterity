# -*- coding: utf-8 -*-
from plone.testing import layered
from transmogrify.dexterity.testing import TRANSMOGRIFY_DEXTERITY_INTEGRATION_TESTING

import doctest
import re
import six
import unittest2 as unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_NDIFF


TESTFILES = (
    "schemaupdater.txt",
    "pipelinescsvsource.txt",
)


class Py23DocChecker(doctest.OutputChecker):
    def __init__(self):
        """Constructor"""

    def transformer_py2_output(self, got):
        """Handles differences in output between Python 2 and Python 3."""
        if six.PY2:
            got = re.sub("u'", "'", got)
            got = re.sub('u"', '"', got)

        return got

    def check_output(self, want, got, optionflags):
        got = self.transformer_py2_output(got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        got = self.transformer_py2_output(got)
        return doctest.OutputChecker.output_difference(self, example, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    filename,
                    optionflags=OPTIONFLAGS,
                    checker=Py23DocChecker(),
                ),
                layer=TRANSMOGRIFY_DEXTERITY_INTEGRATION_TESTING,
            )
            for filename in TESTFILES
        ]
    )
    return suite
