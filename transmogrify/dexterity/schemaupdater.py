from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import Expression

from plone.dexterity.utils import iterSchemata
from plone.uuid.interfaces import IMutableUUID

from z3c.form.interfaces import IValue

from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import classProvides, implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder

from interfaces import IDeserializer

_marker = object()

class DexterityUpdateSection(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.name = name
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.fileskey = options.get('files-key', '_files').strip()
        self.disable_constraints = Expression(options.get('disable-constraints', 'python: False'), 
                                        transmogrifier, name, options)

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

            uuid = item.get('plone.uuid')
            if uuid is not None:
                IMutableUUID(obj).set(str(uuid))

            files = item.setdefault(self.fileskey, {})

            #get all fields for this obj
            for schemata in iterSchemata(obj):
                for name, field in getFieldsInOrder(schemata):
                    #setting value from the blueprint cue
                    value = item.get(name, _marker)
                    if value is _marker:
                        # No value is given from the pipeline,
                        # so we try to set the default value
                        # otherwise we set the missing value
                        default = queryMultiAdapter((
                                obj,
                                obj.REQUEST, # request
                                None, # form
                                field,
                                None, # Widget
                                ), IValue, name='default')
                        if default is not None:
                            default = default.get()
                        if default is None:
                            default = getattr(field, 'default', None)
                        if default is None:
                            try:
                                default = field.missing_value
                            except AttributeError:
                                pass
                        value = default
                    else:
                        deserializer = IDeserializer(field)
                        value = deserializer(value, files, item, self.disable_constraints)
                    field.set(field.interface(obj), value)

            notify(ObjectModifiedEvent(obj))
            yield item
