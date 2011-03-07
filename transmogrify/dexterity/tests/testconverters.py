# -*- coding: utf-8 -*-

import unittest
import zope.testing
import pprint

from plone.app.textfield import RichText

from transmogrify.dexterity import converters
from transmogrify.dexterity.interfaces import ISerializer, IDeserializer

class TestRichTextDeserializer(unittest.TestCase):
    def setUp(test):
        test.pp = pprint.PrettyPrinter(indent=4)
        #TODO: This should read the zcml instead
        zope.component.provideAdapter(converters.RichTextDeserializer)

    def test_string(self):
        """Test default options, should be able to produce an encoded UTF-8
        string of bytes"""
        rtd = IDeserializer(RichText())
        rtv = rtd("café culture",None,None)
        
        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"text/html")
        self.assertEqual(rtv.encoding,"utf-8")

    def test_unicode_string(self):
        """Test that a unicode value gets passed through without
        additional decoding"""
        rtd = IDeserializer(RichText())
        rtv = rtd(u"café culture",None,None)
        
        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"text/html")
        self.assertEqual(rtv.encoding,"utf-8")

    def test_setting_mime_type(self):
        """Test that RichText mime type options affect the RichTextValue"""
        rtd = IDeserializer(RichText(default_mime_type='text/xml',output_mime_type='x-application/pony'))
        rtv = rtd("café culture",None,None)
        
        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType,"x-application/pony")
        self.assertEqual(rtv.mimeType,"text/xml")
        self.assertEqual(rtv.encoding,"utf-8")

    def test_dict_overrides(self):
        """Try using a dict value, ensure that we can override the MIME type,
        and that the MIME type is converted to a string"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'contenttype': u"x-application/pony",
            'data':"café culture",
        },None,None)

        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"x-application/pony","Content type from dict should override default")
        self.assertEqual(rtv.encoding,"utf-8")

    def test_dict_encoding(self):
        """Try using a dict value, ensure that we can override the MIME type"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'data':"caf\xe9 culture",
            'encoding': "latin-1",
        },None,None)

        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xe9 culture")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"text/csv")
        self.assertEqual(rtv.encoding,"latin-1")

    def test_dict_unicode(self):
        """Try using a dict value, ensure that a unicode string passed through
        and can be decoded properly"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'data':u"café culture",
            'encoding': "latin-1",
        },None,None)

        self.assertEqual(rtv.raw,u"café culture")
        self.assertEqual(rtv.raw_encoded,"caf\xe9 culture")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"text/csv")
        self.assertEqual(rtv.encoding,"latin-1")

    def test_filestore(self):
        """Try using a dict with a filestore"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'contenttype': "x-application/cow",
            'data':"caf\xe9 culture",
            'file':'my-lovely-file',
            'encoding': "latin-1",
        },{
            'my-lovely-file': {'data':"greasy spoon"},
        },None)

        self.assertEqual(rtv.raw,u"greasy spoon")
        self.assertEqual(rtv.raw_encoded,"greasy spoon")
        self.assertEqual(rtv.outputMimeType,"text/x-html-safe")
        self.assertEqual(rtv.mimeType,"x-application/cow","Content type from dict should override default")
        self.assertEqual(rtv.encoding,"latin-1")
