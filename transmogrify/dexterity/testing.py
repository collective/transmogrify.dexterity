from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.sections.tests import SampleSource
from plone.app.testing import IntegrationTesting, TEST_USER_ID, setRoles
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.dexterity.fti import DexterityFTI, register
from plone.directives import form
from plone.namedfile.field import NamedFile
from zope import schema
from zope.component import provideUtility
from zope.configuration import xmlconfig
from datetime import date
from zope.interface import classProvides, implements


zptlogo = (
    'GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd'
    '\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6'
    '\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6'
    '\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd'
    '\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9'
    '\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4'
    '\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0'
    '\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb'
    '\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4'
    '\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04'
    '\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4'
    '\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{'
    '\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c'
    '\x866#\'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e"&*-024\xacNq\xba\xbb\xb8h\xbeb'
    '\x00A\x00;')


class ITestSchema(form.Schema):

    foo = schema.TextLine(
        title=u'Foo',
    )

    test_file = NamedFile(
        title=u'File',
    )

    test_date = schema.Date(
        title = u'test_date',
    )


class TransmogrifyDexterityLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import transmogrify.dexterity
        xmlconfig.file('configure.zcml',
            transmogrify.dexterity, context=configurationContext)
        xmlconfig.file('tests.zcml',
            transmogrify.dexterity, context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        setRoles(portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])

        # portal workaround
        self.portal = portal

        # test fti generation
        fti = DexterityFTI('TransmogrifyDexterityFTI')
        fti.schema = 'transmogrify.dexterity.testing.ITestSchema'
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = (
                         'plone.app.dexterity.behaviors.metadata.IBasic',
                         )
        self.portal.portal_types._setObject('TransmogrifyDexterityFTI', fti)
        register(fti)


        # create test schema source and provide it
        class SchemaSource(SampleSource):
            classProvides(ISectionBlueprint)
            implements(ISection)

            def __init__(self, *args, **kw):
                super(SchemaSource, self).__init__(*args, **kw)
                self.sample = (
                    dict(_path='/spam',
                         foo='one value',
                         _type='TransmogrifyDexterityFTI',
                         title='Spam',
                         description='Lorem Ipsum bla bla!',
                         test_file={
                            'data': zptlogo,
                            'filename': 'zptlogo.gif'},
                         test_date='2010-10-12',
                         fieldnotchanged='nochange',
                    ),
                    dict(_path='/two',
                         foo='Bla',
                         _type='TransmogrifyDexterityFTI',
                         title='My Second Object',
                         #description=None, # None is not valid for this field.
                         test_file=zptlogo,
                         _filename="testlogo.gif",
                         test_date=date(2010, 01, 01, ),
                         fieldnotchanged='nochange',
                    ),
                )
        provideUtility(SchemaSource,
            name=u'transmogrify.dexterity.testsource')


TRANSMOGRIFY_DEXTERITY_FIXTURE = TransmogrifyDexterityLayer()
TRANSMOGRIFY_DEXTERITY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TRANSMOGRIFY_DEXTERITY_FIXTURE, ),
    name="TransmogrifyDexterity:Integration")
