from zope.component import queryMultiAdapter
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.utils import Matcher, defaultKeys
from z3c.form.interfaces import IValue
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.file import NamedFile
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IList, IDate, IInt, IBool
from datetime import datetime, date


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

            # not enough info
            if not pathkey:
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
                    if value is not None:
                        # TODO: implements for namedfile field
                        if INamedFileField.providedBy(field):
                            # need a dict with data and filename
                            # or get the filename in a seperated
                            # value from the pipeline
                            if isinstance(value, dict):
                                nfile = NamedFile(
                                    data=value['data'],
                                    filename=value['filename'].decode('utf-8'))
                            else:
                                if '_filename' in item:
                                    nfile = NamedFile(
                                        data=value,
                                        filename=item['_filename'].decode(
                                            'utf-8'))
                                else:
                                    nfile = NamedFile(data=value)
                            field.set(field.interface(obj), nfile)

                        elif IDate.providedBy(field):
                            if isinstance(value, str):
                                try:
                                    value = datetime.strptime(value, "%d.%m.%Y")
                                    value = date(
                                        value.year, value.month, value.day)
                                except ValueError:
                                    continue
                            field.set(field.interface(obj), value)

                        elif IBool.providedBy(field):
                            if isinstance(value, bool):
                                field.set(field.interface(obj), value)
                            elif isinstance(value, basestring) and value.lower()=='true':
                                field.set(field.interface(obj), True)
                            else:
                                field.set(field.interface(obj), False)

                        elif IList.providedBy(field):
                            if IList.providedBy(field):
                                if not isinstance(value, list):
                                    value = filter(
                                        lambda p: not not p,
                                        [p.strip() for p in value.split(';')])
                                field.set(field.interface(obj), value)

                        elif IInt.providedBy(field):
                            field.set(field.interface(obj), int(value))

                        elif isinstance(value, str):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = value.decode('latin1')
                            field.set(field.interface(obj), value)

                        else:
                            field.set(field.interface(obj), value)

                    elif field.get(
                            field.interface(obj)) == field.missing_value \
                                or field.get(field.interface(obj)) == None:

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
