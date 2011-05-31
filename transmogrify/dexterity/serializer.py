import json

from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher

from zope.interface import classProvides, implements


class SerializerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.fileskey = options.get('files-key', '_files').strip()
        self.key = options.get('key', 'content').strip()
        indent = options.get('indent', '4').strip() or None
        if indent is not None:
            indent = int(indent)
        sort_keys = options.get('sort-keys', 'true').strip().lower() == 'true'
        self.encoder = json.JSONEncoder(indent=indent, sort_keys=sort_keys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            fileskey = self.fileskey

            path = item.get(pathkey)
            # not enough info
            if not path:
                yield item
                continue

            if None in item:
                import pdb; pdb.set_trace()
            data = dict((key, value) for key, value in item.iteritems() if not key.startswith('_'))
            if not data:
                yield item
                continue


            files = item.setdefault(fileskey, {})
            files[self.key] = dict(name='_content.json', data=self.encoder.encode(data), contenttype='application/json')

            yield item


class DeserializerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.fileskey = defaultMatcher(options, 'files-key', name, 'files')
        self.key = options.get('key', 'content').strip()

    def __iter__(self):
        for item in self.previous:
            fileskey = self.fileskey(*item.keys())[0]

            files = item.get(fileskey)
            if not files:
                yield item
                continue

            content = files.get(self.key)
            if not content:
                yield item
                continue

            data = json.loads(content['data'])
            item.update(data)

            yield item
