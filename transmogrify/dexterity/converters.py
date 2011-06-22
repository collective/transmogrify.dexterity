import mimetypes
from datetime import datetime

from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.app.textfield.utils import getSiteEncoding

from plone.namedfile.interfaces import INamedField
from plone.supermodel.interfaces import IToUnicode

from zope.component import adapts
from zope.interface import implements
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode

from interfaces import ISerializer, IDeserializer


class NamedFileSerializer(object):
    implements(ISerializer)
    adapts(INamedField)

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        if extra is None:
            extra = ''
        else:
            extra = '_%s' % extra
        fieldname = self.field.__name__
        if hasattr(value, 'open'):
            data = value.open().read()
        else:
            data = value.data
        name = '_field_%s%s_%s' % (fieldname, extra, value.filename)
        filestore[name] = dict(data=data, name=name, contenttype=value.contentType)
        return dict(file=name, filename=value.filename, contenttype=value.contentType)


class NamedFileDeserializer(object):
    implements(IDeserializer)
    adapts(INamedField)

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False):
        if isinstance(value, dict):
            filename = value.get('filename', None)
            contenttype = str(value.get('contenttype', ''))
            file = value.get('file', None)
            if file is not None:
                data = filestore[file]['data']
            else:
                data = value['data']
        elif isinstance(value, str):
            data = value
            filename = item.get('_filename', None)
            contenttype = ''
        else:
            raise ValueError('Unable to convert to named file')
        if isinstance(filename, str):
            filename = filename.decode('utf-8')
        instance = self.field._type(
            data=data,
            filename=filename,
            contentType=contenttype,
            )
        if not disable_constraints:
            self.field.validate(instance)
        return instance


class RichTextSerializer(object):
    implements(ISerializer)
    adapts(IRichText)

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        if extra is None:
            extra = ''
        else:
            extra = '_%s' % extra
        extension = mimetypes.guess_extension(value.mimeType) or ''
        fieldname = self.field.__name__
        name = '_field_%s%s%s' % (fieldname, extra, extension)
        filestore[name] = dict(data=value.raw_encoded, name=name, contenttype=value.mimeType)
        return dict(file=name, contenttype=value.mimeType, encoding=value.encoding)


class RichTextDeserializer(object):
    implements(IDeserializer)
    adapts(IRichText)
    _type = RichTextValue

    def __init__(self, field):
        self.field = field

    def _convert_object(self,obj,encoding):
        """Decode binary strings into unicode objects
        """
        if isinstance(obj, str): return obj.decode(encoding)
        if isinstance(obj, unicode): return obj
        raise ValueError('Unable to convert value to unicode string')
    
    def __call__(self, value, filestore, item, disable_constraints=False):
        if isinstance(value, dict):
            encoding = value.get('encoding', getSiteEncoding())
            contenttype = value.get('contenttype', None)
            if contenttype is not None:
                contenttype = str(contenttype)
            file = value.get('file', None)
            if file is not None:
                data = self._convert_object(filestore[file]['data'],encoding)
            else:
                data = self._convert_object(value['data'],encoding)
        else:
            encoding = getSiteEncoding()
            data = self._convert_object(value,encoding)
            contenttype = None
        if contenttype is None:
            contenttype = self.field.default_mime_type
        instance = self._type(
            raw=data,
            mimeType=contenttype,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
            )
        if not disable_constraints:
            self.field.validate(instance)
        return instance


class CollectionSerializer(object):
    implements(ISerializer)
    adapts(ICollection)    

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        field = self.field
        if field.value_type is not None:
            serializer = ISerializer(self.field.value_type)
        else:
            serializer = DefaultSerializer()
        return [serializer(v, filestore, str(i)) for i, v in enumerate(value)]


class CollectionDeserializer(object):
    implements(IDeserializer)
    adapts(ICollection)    

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False):
        field = self.field
        if value in (None, ''):
            return []
        if isinstance(value, basestring):
            value = [v for v in (v.strip() for v in value.split(';')) if v]
        if field.value_type is not None:
            deserializer = IDeserializer(self.field.value_type)
        else:
            deserializer = DefaultDeserializer()
        value = [deserializer(v, filestore, item, disable_constraints) for v in value]
        value = field._type(value)
        if not disable_constraints:
            self.field.validate(value)
        return value


class DateDeserializer(object):
    implements(IDeserializer)
    adapts(IDate)

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False):
        if isinstance(value, basestring):
            value = datetime.strptime(value, '%Y-%m-%d')
        if isinstance(value, datetime):
            value = value.date()
        if not disable_constraints:
            self.field.validate(value)
        return value


class DefaultSerializer(object):
    implements(ISerializer)
    adapts(IField)

    def __init__(self, field=None):
        self.field = field

    def __call__(self, value, filestore, extra=None):
        BASIC_TYPES = (unicode, int, long, float, bool, type(None))
        if type(value) in BASIC_TYPES:
            pass
        elif self.field is not None:
            value = IToUnicode(self.field).toUnicode(value)
        else:
            raise ValueError('Unable to serialize field value')
        return value


class DefaultDeserializer(object):
    implements(IDeserializer)
    adapts(IField)

    def __init__(self, field):
        self.field = field

    def __call__(self, value, filestore, item, disable_constraints=False):
        field = self.field
        if field is not None:
            if isinstance(value, str):
                value = value.decode('utf-8')
            if isinstance(value, unicode):
                try:
                    value = IFromUnicode(field).fromUnicode(value)
                except ConstraintNotSatisfied:
                    if not disable_constraints:
                        raise ConstraintNotSatisfied(value)
                except TypeError, e:
                    # TODO: This TypeError may happen because zope.schema._field.Choice._validate
                    # tries to iterate over a vocabulary factory without calling it
                    if not disable_constraints:
                        raise e
            if not disable_constraints:
                self.field.validate(value)
        return value
