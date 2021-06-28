from zope.interface import Interface


class ISerializer(Interface):

    def __call__(value, filestore, extra=None):
        """Convert to a serializable reprentation
        """


class IDeserializer(Interface):

    def __call__(value, filestore, item):
        """Convert to a field value
        """
