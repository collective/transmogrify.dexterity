from zope.component import queryMultiAdapter
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import Matcher, defaultKeys
from z3c.form.interfaces import IValue
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IList, IDate, IInt, IBool
from datetime import datetime


class DexterityUpdateSection(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.name = name

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]

            if not pathkey:         # not enough info
                yield item
                continue

            path = item[pathkey]

            obj = self.context.unrestrictedTraverse(
                path.encode().lstrip('/'), None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            #get all fields for this obj
            for schemata in iterSchemata(obj):
                for name, field in getFieldsInOrder(schemata):

                    #setting value from the blueprint cue
                    value = item.get(name)

                    if value:
                        if IDate.providedBy(field):
                            if isinstance(value, str):
                                value = datetime.strptime(value, "%d.%m.%Y")
                            field.set(field.interface(obj), value)

                        elif IBool.providedBy(field):
                            if value.lower()=='true':
                                field.set(field.interface(obj), True)
                            else:
                                field.set(field.interface(obj), False)

                        elif IList.providedBy(field):
                            if IList.providedBy(field):
                                v = filter(
                                    lambda p: not not p,
                                    [p.strip() for p in value.split(';')])
                                field.set(field.interface(obj), v)

                        elif IInt.providedBy(field):
                            field.set(field.interface(obj), int(value))
                        else:
                            field.set(field.interface(obj), value)
                    else:
                        # No value is given from the blueprint cue,
                        # so we try to set the default value
                        # otherwise we set the missing value

                        default = queryMultiAdapter((
                                obj,
                                obj.REQUEST, # request
                                None, # form
                                field,
                                None, # Widget
                                ), IValue, name='default')
                        if default!=None:
                            default = default.get()
                        if default==None:
                            default = getattr(field, 'default', None)
                        if default==None:
                            try:
                                default = field.missing_value
                            except:
                                pass
                        field.set(field.interface(obj), default)
            yield item
