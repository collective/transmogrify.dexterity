# -*- coding: utf-8 -*-
from plone.app.textfield import RichText, RichTextValue
from plone.supermodel import model
from transmogrify.dexterity.interfaces import ISerializer, IDeserializer
from z3c.form.object import registerFactoryAdapter
from zope import schema, interface
import unittest
import zope.testing


class ITestObjectA(model.Schema):
    fish = schema.TextLine(
        title=u'Fish',
        default=u"",
        required=False)


@interface.implementer(ITestObjectA)
class TestObjectA(object):
    fish = schema.fieldproperty.FieldProperty(ITestObjectA['fish'])
registerFactoryAdapter(ITestObjectA, TestObjectA)


class ITestObjectB(model.Schema):
    title = schema.TextLine(
        title=u'Title',
        default=u"",
        required=False)
    cowtent = RichText(
        title=u"Text",
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=('text/html', 'scroll/dead-sea'),
        default=u"",
        required=False)


@interface.implementer(ITestObjectB)
class TestObjectB(object):
    title = schema.fieldproperty.FieldProperty(ITestObjectB['title'])
    cowtent = schema.fieldproperty.FieldProperty(ITestObjectB['cowtent'])
registerFactoryAdapter(ITestObjectB, TestObjectB)


class TestObjectDeserializer(unittest.TestCase):

    def setUp(test):
        # TODO: Should be importing ZCML
        from transmogrify.dexterity import converters
        zope.component.provideAdapter(converters.ObjectDeserializer)
        zope.component.provideAdapter(converters.RichTextDeserializer)
        zope.component.provideAdapter(converters.DefaultDeserializer)

    def deserialize(self, des, input):
        if des.field.schema == ITestObjectA:
            input["_class"] = "transmogrify.dexterity.tests.testconverters_object.TestObjectA"  # noqa
        elif des.field.schema == ITestObjectB:
            input["_class"] = "transmogrify.dexterity.tests.testconverters_object.TestObjectB"  # noqa
        return des(input, None, None)

    def test_failures(self):
        desA = IDeserializer(schema.Object(schema=ITestObjectA))

        # Have to provide something
        with self.assertRaisesRegexp(ValueError, "dict"):
            desA(None, None, None)

        # Dict needs to provide class
        with self.assertRaisesRegexp(ValueError, "_class"):
            desA(dict(), None, None)

        # _class needs to implement ITestObjectA
        with self.assertRaisesRegexp(ValueError, "TestObjectDeserializer"):
            desA(dict(_class="transmogrify.dexterity.tests.testconverters_object.TestObjectDeserializer"), None, None)  # noqa

        # Extra values not allowed
        with self.assertRaisesRegexp(ValueError, "fart"):
            self.deserialize(desA, dict(fish=u'moo', fart="yes"))

    def test_deserialise(self):
        desA = IDeserializer(schema.Object(schema=ITestObjectA))
        desB = IDeserializer(schema.Object(schema=ITestObjectB))

        obj = self.deserialize(desA, dict(fish=u'moo'))
        self.assertEqual(obj.__class__, TestObjectA)
        self.assertEqual(obj.fish, u'moo')

        # We recurseivly deserialize
        obj = self.deserialize(desB, dict(
            title=u'A nice section',
            cowtent=dict(data=u'Some nice text', contenttype='scroll/dead-sea')
        ))
        self.assertEqual(obj.__class__, TestObjectB)
        self.assertEqual(obj.title, u'A nice section')
        self.assertEqual(obj.cowtent.__class__, RichTextValue)
        self.assertEqual(obj.cowtent.raw, u'Some nice text')
        self.assertEqual(obj.cowtent.mimeType, 'scroll/dead-sea')

        # Missing values are okay
        obj = self.deserialize(desB, dict(
            title=u'Another section',
        ))
        self.assertEqual(obj.__class__, TestObjectB)
        self.assertEqual(obj.title, u'Another section')
        self.assertEqual(obj.cowtent.__class__, RichTextValue)
        self.assertEqual(obj.cowtent.raw, u'')
        self.assertEqual(obj.cowtent.mimeType, 'text/html')


class TestObjectSerializer(unittest.TestCase):

    def setUp(test):
        # TODO: Should be importing ZCML
        from transmogrify.dexterity import converters
        zope.component.provideAdapter(converters.ObjectSerializer)
        zope.component.provideAdapter(converters.RichTextSerializer)
        zope.component.provideAdapter(converters.DefaultSerializer)
        zope.component.provideAdapter(converters.ObjectDeserializer)
        zope.component.provideAdapter(converters.RichTextDeserializer)
        zope.component.provideAdapter(converters.DefaultDeserializer)

    def test_serialize(self):
        desB = IDeserializer(schema.Object(schema=ITestObjectB))
        serA = ISerializer(schema.Object(schema=ITestObjectA))
        serB = ISerializer(schema.Object(schema=ITestObjectB))

        obj = TestObjectA()
        obj.fish = u"haddock"
        self.assertEqual(
            serA(
                obj,
                None),
            dict(
                _class="transmogrify.dexterity.tests.testconverters_object.TestObjectA",  # noqa
                fish=u"haddock",
            ))

        # Recurse into attributes
        filestore = {}
        obj = desB(
            dict(
                title=u'A hairy section',
                cowtent=dict(
                    data=u'Some nice text',
                    contenttype='scroll/dead-sea'),
                _class="transmogrify.dexterity.tests.testconverters_object.TestObjectB",  # noqa
            ),
            filestore,
            None)
        self.assertEqual(
            serB(
                obj,
                filestore),
            dict(
                _class="transmogrify.dexterity.tests.testconverters_object.TestObjectB",  # noqa
                title=u'A hairy section',
                cowtent=dict(
                    file='_field_cowtent_cowtent',
                    encoding='utf-8',
                    contenttype='scroll/dead-sea',
                ),
            ))
