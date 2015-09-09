# -*- coding: utf-8 -*-
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from plone.app.textfield import RichText
from plone.formwidget.contenttree import ObjPathSourceBinder
from transmogrify.dexterity import converters
from transmogrify.dexterity.interfaces import IDeserializer
from transmogrify.dexterity.testing import TRANSMOGRIFY_DEXTERITY_FUNCTIONAL_TESTING
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.schema import Datetime
import pprint
import unittest
import zope.testing


class TestRelationDeserializer(unittest.TestCase):

    layer = TRANSMOGRIFY_DEXTERITY_FUNCTIONAL_TESTING

    relation = RelationChoice(
        title=u"Relation",
        source=ObjPathSourceBinder(),
        required=False,
    )

    relation_list = RelationList(
        title=u"Relation List",
        default=[],
        value_type=RelationChoice(title=u"Relation",
                                  source=ObjPathSourceBinder()),
        required=False,
    )

    def test_deserialize_relation(self):
        folder = create(Builder('folder'))
        deserializer = IDeserializer(self.relation)
        value = deserializer(folder, None, None)

        self.assertTrue(isinstance(value, RelationValue))
        self.assertEqual(folder, value.to_object)

    def test_deserialize_none_relation(self):
        deserializer = IDeserializer(self.relation)
        value = deserializer(None, None, None)

        self.assertIsNone(value)

    def test_deserialize_non_int_id_relation(self):
        deserializer = IDeserializer(self.relation)
        value = deserializer("bar", None, None)

        self.assertEqual("bar", value)

    def test_deserialize_relation_list(self):
        folder = create(Builder('folder'))
        deserializer = IDeserializer(self.relation_list)
        value = deserializer([folder], None, None)

        self.assertEqual(1, len(value))
        self.assertTrue(isinstance(value[0], RelationValue))
        self.assertEqual(folder, value[0].to_object)

    def test_deserialize_empty_relation_list(self):
        deserializer = IDeserializer(self.relation_list)
        value = deserializer([], None, None)

        self.assertEqual(0, len(value))
        self.assertEqual([], value)

    def test_deserialize_none_relation_list(self):
        deserializer = IDeserializer(self.relation_list)
        value = deserializer(None, None, None)

        self.assertEqual(0, len(value))
        self.assertEqual([], value)

    def test_deserialize_non_int_id_relation_list(self):
        deserializer = IDeserializer(self.relation_list)
        value = deserializer(["foo"], None, None)

        self.assertEqual(1, len(value))
        self.assertEqual(["foo"], value)


class TestRichTextDeserializer(unittest.TestCase):

    def setUp(test):
        test.pp = pprint.PrettyPrinter(indent=4)
        # TODO: This should read the zcml instead
        zope.component.provideAdapter(converters.RichTextDeserializer)

    def test_string(self):
        """Test default options, should be able to produce an encoded UTF-8
        string of bytes"""
        rtd = IDeserializer(RichText())
        rtv = rtd("café culture", None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(rtv.mimeType, "text/html")
        self.assertEqual(rtv.encoding, "utf-8")

    def test_unicode_string(self):
        """Test that a unicode value gets passed through without
        additional decoding"""
        rtd = IDeserializer(RichText())
        rtv = rtd(u"café culture", None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(rtv.mimeType, "text/html")
        self.assertEqual(rtv.encoding, "utf-8")

    def test_setting_mime_type(self):
        """Test that RichText mime type options affect the RichTextValue"""
        rtd = IDeserializer(
            RichText(
                default_mime_type='text/xml',
                output_mime_type='x-application/pony'))
        rtv = rtd("café culture", None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType, "x-application/pony")
        self.assertEqual(rtv.mimeType, "text/xml")
        self.assertEqual(rtv.encoding, "utf-8")

    def test_dict_overrides(self):
        """Try using a dict value, ensure that we can override the MIME type,
        and that the MIME type is converted to a string"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'contenttype': u"x-application/pony",
            'data': "café culture",
        }, None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xc3\xa9 culture")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(
            rtv.mimeType,
            "x-application/pony",
            "Content type from dict should override default")
        self.assertEqual(rtv.encoding, "utf-8")

    def test_dict_encoding(self):
        """Try using a dict value, ensure that we can override the MIME type"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'data': "caf\xe9 culture",
            'encoding': "latin-1",
        }, None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xe9 culture")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(rtv.mimeType, "text/csv")
        self.assertEqual(rtv.encoding, "latin-1")

    def test_dict_unicode(self):
        """Try using a dict value, ensure that a unicode string passed through
        and can be decoded properly"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'data': u"café culture",
            'encoding': "latin-1",
        }, None, None)

        self.assertEqual(rtv.raw, u"café culture")
        self.assertEqual(rtv.raw_encoded, "caf\xe9 culture")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(rtv.mimeType, "text/csv")
        self.assertEqual(rtv.encoding, "latin-1")

    def test_filestore(self):
        """Try using a dict with a filestore"""
        rtd = IDeserializer(RichText(default_mime_type='text/csv'))
        rtv = rtd({
            'contenttype': "x-application/cow",
            'data': "caf\xe9 culture",
            'file': 'my-lovely-file',
            'encoding': "latin-1",
        }, {
            'my-lovely-file': {'data': "greasy spoon"},
        }, None)

        self.assertEqual(rtv.raw, u"greasy spoon")
        self.assertEqual(rtv.raw_encoded, "greasy spoon")
        self.assertEqual(rtv.outputMimeType, "text/x-html-safe")
        self.assertEqual(
            rtv.mimeType,
            "x-application/cow",
            "Content type from dict should override default")
        self.assertEqual(rtv.encoding, "latin-1")


class TestDatetimeDeserializer(unittest.TestCase):

    layer = TRANSMOGRIFY_DEXTERITY_FUNCTIONAL_TESTING

    def setUp(test):
        test.pp = pprint.PrettyPrinter(indent=4)
        # TODO: This should read the zcml instead
        zope.component.provideAdapter(converters.DatetimeDeserializer)

    def test_datetime_deserializer(self):
        deserializer = IDeserializer(Datetime())
        value = deserializer('2015-12-31 17:59:59', None, None)
        self.assertEqual(
            datetime(2015, 12, 31, 17, 59, 59),
            value
        )

    def test_datetime_deserializer_for_not_required_datetime(self):
        field = Datetime()
        field.required = False
        deserializer = IDeserializer(field)
        value = deserializer('None', None, None)

        self.assertEqual(None, value)
