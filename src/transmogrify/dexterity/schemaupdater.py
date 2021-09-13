# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import Expression
from plone.app.dexterity.behaviors.metadata import DublinCore
from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.uuid.interfaces import IMutableUUID
from transmogrify.dexterity import PLONE_VERSION
from transmogrify.dexterity.interfaces import IDeserializer
from z3c.form import interfaces
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import implementer
from zope.interface import provider
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder

import logging
import six


_marker = object()


PLONE_43 = PLONE_VERSION == 4.3


dublin_core_fields = [
    (
        name,
        field,
    )
    for name, field in getFieldsInOrder(IDublinCore)
]


@provider(ISectionBlueprint)
@implementer(ISection)
class DexterityUpdateSection(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = (
            transmogrifier.context if transmogrifier.context else getSite()
        )  # noqa
        self.name = name
        self.pathkey = defaultMatcher(options, "path-key", name, "path")
        self.fileskey = options.get("files-key", "_files").strip()
        self.disable_constraints = Expression(
            options.get("disable-constraints", "python: False"),
            transmogrifier,
            name,
            options,
        )

        # if importing from collective.jsonify exported json structures, there
        # is an datafield entry for binary data, which' prefix can be
        # configured.
        self.datafield_prefix = options.get("datafield-prefix", "_datafield_")

        # create logger
        if options.get("logger"):
            self.logger = logging.getLogger(options["logger"])
            self.loglevel = getattr(logging, options["loglevel"], None)
            if self.loglevel is None:
                # Assume it's an integer:
                self.loglevel = int(options["loglevel"])
            self.logger.setLevel(self.loglevel)
            self.log = lambda s: self.logger.log(self.loglevel, s)
        else:
            self.log = None

    def get_value_from_pipeline(self, field, item):
        name = field.getName()
        # setting value from the blueprint cue
        value = item.get(name, _marker)
        if value is _marker:
            # Also try _datafield_FIELDNAME structure from jsonify
            value = item.get("_datafield_%s" % name, _marker)
        if value is not _marker:
            # Value was given in pipeline, so set it
            deserializer = IDeserializer(field)
            if IRichText.providedBy(field) and "_content_type_%s" % name in item:
                # change jsonify structure to one we understand
                value = {"contenttype": item["_content_type_%s" % name], "data": value}
            files = item.setdefault(self.fileskey, {})
            value = deserializer(
                value, files, item, self.disable_constraints, logger=self.log
            )
        return value

    def determine_default_value(self, obj, field):
        """Determine the default to be set for a field that didn't receive
        a value from the pipeline.
        """
        default = queryMultiAdapter(
            (
                obj,
                obj.REQUEST,  # request
                None,  # form
                field,
                None,  # Widget
            ),
            interfaces.IValue,
            name="default",
        )
        if default is not None:
            default = default.get()
        if default is None:
            default = getattr(field, "default", None)
        if default is None:
            try:
                default = field.missing_value
            except AttributeError:
                pass
        return default

    def update_field(self, obj, field, item, extra_dublin_core=False):
        if field.readonly:
            return

        name = field.getName()
        value = self.get_value_from_pipeline(field, item)
        if value is not _marker:
            # In Plone 5+ if we try to update to the same id, Plone will
            # try to put a different id from the folder object ids.
            # As the object is also in the folder, it will receive a different
            # id. For example, if we try to update the id to new-id, the id
            # the object will get is new-id-1. So we can't update to the same
            # id.
            if name != "id" or value != obj.id:
                if extra_dublin_core:
                    dublin_core = DublinCore(obj)
                    field.set(dublin_core, value)
                else:
                    field.set(field.interface(obj), value)
            return

        if extra_dublin_core:
            # The object doesn't have the DublinCore behavior and DublinCore
            # field didn't come in json. In this situation we don't try to set
            # a default value.
            return

        # Get the field's current value, if it has one then leave it alone
        value = getMultiAdapter((obj, field), interfaces.IDataManager).query()

        # Fix default description to be an empty unicode instead of
        # an empty bytestring because of this bug:
        # https://github.com/plone/plone.dexterity/pull/33
        if name == "description" and value == "":
            field.set(field.interface(obj), u"")
            return

        if not (value is field.missing_value or value is interfaces.NO_VALUE):
            return

        # Finally, set a default value if nothing is set so far
        default = self.determine_default_value(obj, field)
        field.set(field.interface(obj), default)

    def get_fields(self, obj):
        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                yield name, field

    def get_extras_dublin_core_fields(self, obj):
        """Returns fields of IDublinCore interface, which are not in the
        object's behaviors.
        """
        fields = list(self.get_fields(obj))
        for name_field in dublin_core_fields:
            if name_field not in fields:
                yield name_field

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            # not enough info
            if not pathkey:
                yield item
                continue

            path = item[pathkey]
            # Skip the Plone site object itself
            if not path:
                yield item
                continue

            if six.PY2:
                path = path.encode()

            obj = self.context.unrestrictedTraverse(path.lstrip("/"), None)

            if not IDexterityContent.providedBy(obj):
                # Path doesn't exist
                # obj can not only be None, but also the value of an attribute,
                # which is returned by traversal.
                yield item
                continue

            uuid = item.get("plone.uuid")
            if uuid is not None:
                IMutableUUID(obj).set(str(uuid))

            creators = None

            # For all fields in the schema, update in roughly the same way
            # z3c.form.widget.py would
            for name, field in self.get_fields(obj):
                if PLONE_43 and name == "creators":
                    creators = field
                    continue
                self.update_field(obj, field, item)

            extra_creators = None

            # Updates fields of IDublinCore interface, which are not in the
            # object's behaviors.
            for name, field in self.get_extras_dublin_core_fields(obj):
                if PLONE_43 and name == "creators":
                    extra_creators = field
                    continue
                self.update_field(obj, field, item, extra_dublin_core=True)

            notify(ObjectModifiedEvent(obj))

            # BBB:In Plone 4.3 the notify(ObjectModifiedEvent(obj)) causes the
            # user runing the migration to be added to the creators. So we need
            # to set the creators after the event call, so the creators only
            # have the values that are in json.
            if creators:
                self.update_field(obj, creators, item)
            if extra_creators:
                self.update_field(
                    obj,
                    extra_creators,
                    item,
                    extra_dublin_core=True,
                )
            yield item
