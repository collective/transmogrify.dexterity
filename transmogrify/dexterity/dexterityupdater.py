from zope import event
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import Matcher, defaultKeys

from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.event import ObjectEditedEvent
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IList, IDate
from datetime import datetime

class DexterityUpdateSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)
    
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.name = name
        
        if 'path-key' in options:
            pathkeys = options['paht-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)


    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            
            if not pathkey:         # not enough info
                yield item; continue

            path = item[pathkey]

            obj = self.context.unrestrictedTraverse(path.encode().lstrip('/'), None)
            if obj is None:         # path doesn't exist
                yield item; continue

            #get all fields for this obj
            fields = {}
            for schemata in iterSchemata(obj):
                for name, field in getFieldsInOrder(schemata):
                    fields[name] = field
            for k,v in item.iteritems():
                if k.startswith('_'):
                    continue
                if k not in fields:
                    continue
                field = fields[k]

                #boolean field
                if v is None or v == '':
                    continue
                if v.lower()=='true':
                    field.set(field.interface(obj), True)
                    continue
                elif v.lower()=='false':
                    field.set(field.interface(obj), False)
                    continue
                # listfield
                if IList.providedBy(field):
                    v = filter(lambda p:not not p,
                               [p.strip() for p in v.split(',')])
                    field.set(field.interface(obj), v)
                # datefield
                elif IDate.providedBy(field):
                    v = datetime.strptime(v,"%d.%m.%Y")
                    field.set(field.interface(obj), v)
                # integer check
                elif v.isdigit():
                    field.set(field.interface(obj), int(v))
                else:
                    field.set(field.interface(obj), v)

            if IBaseObject.providedBy(obj):
                changed = False
                is_new_object = obj.checkCreationFlag()
                for k,v in item.iteritems():
                    if k.startswith('_'):
                        continue
                    field = obj.getField(k)
                    if field is None:
                        continue
                    field.set(obj, v)
                    changed = True
                obj.unmarkCreationFlag()

                if is_new_object:
                    event.notify(ObjectInitializedEvent(obj))
                    obj.at_post_create_script()
                elif changed:
                    event.notify(ObjectEditedEvent(obj))
                    obj.at_post_edit_script()

            yield item



        