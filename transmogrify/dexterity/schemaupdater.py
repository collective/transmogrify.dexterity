import logging
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import Expression
from plone.dexterity.utils import iterSchemata
from plone.uuid.interfaces import IMutableUUID
from z3c.form import interfaces
from zope.component import queryMultiAdapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import classProvides
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
from interfaces import IDeserializer


_marker = object()


@implementer(ISection)
class DexterityUpdateSection(object):
    classProvides(ISectionBlueprint)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.name = name
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.fileskey = options.get('files-key', '_files').strip()
        self.disable_constraints = Expression(
            options.get('disable-constraints', 'python: False'),
            transmogrifier,
            name,
            options,
        )

        # create logger
        if options.get('logger'):
            self.logger = logging.getLogger(options['logger'])
            self.loglevel = getattr(logging, options['loglevel'], None)
            if self.loglevel is None:
                # Assume it's an integer:
                self.loglevel = int(options['loglevel'])
            self.logger.setLevel(self.loglevel)
            self.log = lambda s: self.logger.log(self.loglevel, s)
        else:
            self.log = None

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

            # For all fields in the schema, update in roughly the same way
            # z3c.form.widget.py would
            for schemata in iterSchemata(obj):
                for name, field in getFieldsInOrder(schemata):
                    if field.readonly:
                        continue
                    #setting value from the blueprint cue
                    value = item.get(name, _marker)
                    if value is not _marker:
                        # Value was given in pipeline, so set it
                        deserializer = IDeserializer(field)
                        value = deserializer(
                            value,
                            files,
                            item,
                            self.disable_constraints,
                            logger=self.log,
                        )
                        field.set(field.interface(obj), value)
                        continue

                    # Get the widget's current value, if it has one then leave
                    # it alone
                    value = getMultiAdapter(
                        (obj, field),
                        interfaces.IDataManager).query()
                    if not(value is field.missing_value
                           or value is interfaces.NO_VALUE):
                        continue

                    # Finally, set a default value if nothing is set so far
                    default = queryMultiAdapter((
                        obj,
                        obj.REQUEST,  # request
                        None,  # form
                        field,
                        None,  # Widget
                    ), interfaces.IValue, name='default')
                    if default is not None:
                        default = default.get()
                    if default is None:
                        default = getattr(field, 'default', None)
                    if default is None:
                        try:
                            default = field.missing_value
                        except AttributeError:
                            pass
                    field.set(field.interface(obj), default)

            notify(ObjectModifiedEvent(obj))
            yield item
