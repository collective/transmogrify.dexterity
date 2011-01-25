from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import Matcher, defaultKeys, defaultMatcher

from plone.dexterity.utils import iterSchemata
from plone.uuid.interfaces import IUUID
from zope.schema import getFieldsInOrder

from interfaces import ISerializer


class DexterityReaderSection(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

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

            # path doesn't exist
            if obj is None:
                yield item
                continue

            uuid = IUUID(obj, None)
            if uuid is not None:
                item['plone.uuid'] = uuid

            files = item.setdefault(self.fileskey, {})

            #get all fields for this obj
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
