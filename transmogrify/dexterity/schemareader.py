from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from transmogrify.dexterity.interfaces import ISerializer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.uuid.interfaces import IUUID
from zope.interface import classProvides
from zope.interface import implementer
from zope.schema import getFieldsInOrder


@implementer(ISection)
class DexterityReaderSection(object):
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.name = name
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.fileskey = options.get('files-key', '_files').strip()

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            # not enough info
            if not pathkey:
                yield item
                continue

            path = item[pathkey]
            # Skip the Plone site object itself
            if not path:
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                path.encode().lstrip('/'), None)

            if not IDexterityContent.providedBy(obj):
                # Path doesn't exist
                # obj can not only be None, but also the value of an attribute,
                # which is returned by traversal.
                yield item
                continue

            uuid = IUUID(obj, None)
            if uuid is not None:
                item['plone.uuid'] = uuid

            files = item.setdefault(self.fileskey, {})

            # get all fields for this obj
            for schemata in iterSchemata(obj):
                for name, field in getFieldsInOrder(schemata):
                    try:
                        value = field.get(schemata(obj))
                    except AttributeError:
                        continue
                    if value is field.missing_value:
                        continue
                    serializer = ISerializer(field)
                    item[name] = serializer(value, files)

            yield item
