from datetime import datetime
from DateTime import DateTime
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.interfaces import INamedField
from plone.supermodel.interfaces import IToUnicode
from transmogrify.dexterity.interfaces import IDeserializer
from transmogrify.dexterity.interfaces import ISerializer
from z3c.relationfield.interfaces import IRelation
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.relation import RelationValue
from zope.component import adapter
from zope.component import queryUtility
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IObject

import base64
import mimetypes


ENCODING = "utf-8"


@implementer(ISerializer)
@adapter(INamedField)
class NamedFileSerializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        if extra is None:
            extra = ""
        else:
            extra = f"_{extra}"
        fieldname = self.field.__name__
        if hasattr(value, "open"):
            data = value.open().read()
        else:
            data = value.data
        name = f"_field_{fieldname}{extra}_{value.filename}"
        filestore[name] = dict(data=data, name=name, contenttype=value.contentType)
        return dict(file=name, filename=value.filename, contenttype=value.contentType)


@implementer(IDeserializer)
@adapter(INamedField)
class NamedFileDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        if isinstance(value, dict):
            filename = value.get("filename", None)
            contenttype = str(value.get("contenttype", ""))
            if not contenttype:
                # like in jsonify
                contenttype = str(value.get("content_type", ""))
            file = value.get("file", None)
            if file is not None:
                data = filestore[file]["data"]
            else:
                if value.get("encoding", None) == "base64":
                    # collective.jsonify encodes base64
                    data = base64.b64decode(value["data"])
                else:
                    data = value["data"]

        elif isinstance(value, str):
            data = value
            filename = item.get("_filename", None)
            contenttype = ""
        else:
            raise ValueError("Unable to convert to named file")
        instance = self.field._type(
            data=data,
            filename=filename,
            contentType=contenttype,
        )
        try:
            self.field.validate(instance)
        except Exception as e:
            if not disable_constraints:
                raise e
            else:
                if logger:
                    field_name = self.field.__name__
                    path = item["_path"]
                    logger(
                        f"NamedFileDeserializer: {field_name} is invalid in {path}: {e}"
                    )
        return instance


@implementer(ISerializer)
@adapter(IRichText)
class RichTextSerializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        extra = "" if extra is None else f"_{extra}"
        extension = mimetypes.guess_extension(value.mimeType) or ""
        fieldname = self.field.__name__
        name = f"_field_{fieldname}{extra}{extension}"
        filestore[name] = dict(
            data=value.raw_encoded, name=name, contenttype=value.mimeType
        )
        return dict(file=name, contenttype=value.mimeType, encoding=value.encoding)


@implementer(IDeserializer)
@adapter(IRichText)
class RichTextDeserializer:
    _type = RichTextValue

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        if isinstance(value, dict):
            encoding = value.get("encoding", ENCODING)
            contenttype = value.get("contenttype", None)
            if contenttype is not None:
                contenttype = str(contenttype)
            file = value.get("file", None)
            if file is not None:
                data = filestore[file]["data"]
            else:
                data = value["data"]
        else:
            encoding = ENCODING
            data = value
            contenttype = None
        if contenttype is None:
            contenttype = self.field.default_mime_type
        instance = self._type(
            raw=data,
            mimeType=contenttype,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
        )
        try:
            self.field.validate(instance)
        except Exception as e:
            if not disable_constraints:
                raise e
            else:
                if logger:
                    field_name = self.field.__name__
                    path = item["_path"]
                    logger(
                        f"RichTextDeserializer: {field_name} is invalid in {path}: {e}"
                    )
        return instance


@implementer(ISerializer)
@adapter(IObject)
class ObjectSerializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=""):
        out = {
            "_class": "%s.%s"
            % (
                value.__class__.__module__,
                value.__class__.__name__,
            )
        }
        for k in self.field.schema:
            serializer = ISerializer(self.field.schema[k])
            out[k] = serializer(getattr(value, k), filestore, extra + k)
        return out


@implementer(IDeserializer)
@adapter(IObject)
class ObjectDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        if not isinstance(value, dict):
            raise ValueError("Need a dict to convert")
        if not value.get("_class", None):
            try:
                # NB: datagridfield creates it's own Serializer, but falls
                # back to this Deserializer. _class will be missing in this
                # case.
                from collective.z3cform.datagridfield.row import DictRow

                if isinstance(self.field, DictRow):
                    # NB: Should be recursing into the dict and deserializing,
                    # but that can be fixed within datagridfield
                    return DefaultDeserializer(self.field)(
                        value,
                        filestore,
                        item,
                        disable_constraints=disable_constraints,
                        logger=logger,
                    )
            except ImportError:
                pass
            raise ValueError("_class is missing")

        # Import _class and create instance, if it implments what we need
        klass = resolve(value["_class"])
        if not self.field.schema.implementedBy(klass):
            raise ValueError(
                "%s does not implemement %s"
                % (
                    value["_class"],
                    self.field.schema,
                )
            )
        instance = klass()

        # Add each key from value to instance
        for (k, v) in value.items():
            if k == "_class":
                continue
            if not hasattr(instance, k):
                raise ValueError("%s is not an object attribute" % k)
            if v is None:
                setattr(instance, k, None)
                continue

            if k in self.field.schema:
                deserializer = IDeserializer(self.field.schema[k])
            else:
                deserializer = DefaultDeserializer(None)
            setattr(
                instance,
                k,
                deserializer(
                    v,
                    filestore,
                    item,
                    disable_constraints=disable_constraints,
                    logger=logger,
                ),
            )

        if not disable_constraints:
            self.field.validate(instance)
        return instance


@implementer(ISerializer)
@adapter(ICollection)
class CollectionSerializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        field = self.field
        if field.value_type is not None:
            serializer = ISerializer(self.field.value_type)
        else:
            serializer = DefaultSerializer()
        return [serializer(v, filestore, str(i)) for i, v in enumerate(value)]


@implementer(IDeserializer)
@adapter(ICollection)
class CollectionDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        field = self.field
        if value in (None, ""):
            return []
        if isinstance(value, str):
            value = [v for v in (v.strip() for v in value.split(";")) if v]
        if field.value_type is not None:
            deserializer = IDeserializer(self.field.value_type)
        else:
            deserializer = DefaultDeserializer(None)
        value = [
            deserializer(v, filestore, item, disable_constraints, logger=logger)
            for v in value
        ]
        value = field._type(value)
        try:
            self.field.validate(value)
        except Exception as e:
            if not disable_constraints:
                raise e
            else:
                if logger:
                    field_name = self.field.__name__
                    path = item["_path"]
                    logger(
                        f"CollectionDeserializer: {field_name} is invalid in {path}: {e}"
                    )
        return value


@implementer(IDeserializer)
@adapter(IDate)
class DateDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        if isinstance(value, str):
            value = None if value in ("", "None") else DateTime(value).asdatetime()
        if isinstance(value, datetime):
            value = value.date()
        try:
            self.field.validate(value)
        except Exception as e:
            if not disable_constraints:
                raise e
            else:
                if logger:
                    field_name = self.field.__name__
                    path = item["_path"]
                    logger(f"DateDeserializer: {field_name} is invalid in {path}: {e}")
        return value


@implementer(IDeserializer)
@adapter(IDatetime)
class DatetimeDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        if isinstance(value, str):
            value = None if value in ("", "None") else DateTime(value).asdatetime()
        try:
            self.field.validate(value)
        except Exception as e:
            if not disable_constraints:
                raise e
            else:
                if logger:
                    field_name = self.field.__name__
                    path = item["_path"]
                    logger(
                        f"DatetimeDeserializer: {field_name} is invalid in {path}: {e}"
                    )
        return value


@implementer(ISerializer)
@adapter(IField)
class DefaultSerializer:
    def __init__(self, field=None):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        BASIC_TYPES = (str, int, float, bool, type(None))
        if type(value) in BASIC_TYPES:
            pass
        elif self.field is not None:
            value = IToUnicode(self.field).toUnicode(value)
        else:
            raise ValueError("Unable to serialize field value")
        return value


@implementer(IDeserializer)
@adapter(IField)
class DefaultDeserializer:
    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        field = self.field
        if field is not None:
            try:
                if isinstance(value, str):
                    value = IFromUnicode(field).fromUnicode(value)
                self.field.validate(value)
            except Exception as e:
                if not disable_constraints:
                    raise e
                else:
                    if logger:
                        field_name = self.field.__name__
                        path = item["_path"]
                        logger(
                            f"DefaultDeserializer: {field_name} is invalid in {path}: {e}"
                        )
        return value


@implementer(IDeserializer)
@adapter(IRelation)
class RelationDeserializer:

    default_value = None

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False, logger=None):
        field = self.field
        if field is None:
            return None

        if not value:
            return self.default_value

        self.intids = queryUtility(IIntIds)
        if self.intids is None:
            return value

        return self.deserialize(value)

    def deserialize(self, value):
        if isinstance(value, str):
            content = uuidToObject(value)
            if content:
                return RelationValue(self.intids.getId(content))
            else:
                return
        int_id = self.intids.queryId(value)
        if int_id is None:
            return value

        return RelationValue(int_id)


@implementer(IDeserializer)
@adapter(IRelationList)
class RelationListDeserializer(RelationDeserializer):

    default_value = []

    def deserialize(self, value):
        result = []
        for obj in value:
            result.append(super().deserialize(obj))
        return result
