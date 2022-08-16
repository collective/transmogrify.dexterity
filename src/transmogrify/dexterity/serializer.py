from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import provider

import json


@provider(ISectionBlueprint)
@implementer(ISection)
class SerializerSection:
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = (
            transmogrifier.context if transmogrifier.context else getSite()
        )  # noqa

        self.pathkey = defaultMatcher(options, "path-key", name, "path")
        self.fileskey = options.get("files-key", "_files").strip()
        self.key = options.get("key", "content").strip()
        indent = options.get("indent", "4").strip() or None
        if indent is not None:
            indent = int(indent)
        sort_keys = options.get("sort-keys", "true").strip().lower() == "true"
        self.encoder = json.JSONEncoder(indent=indent, sort_keys=sort_keys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            fileskey = self.fileskey

            path = item.get(pathkey)
            # not enough info
            if not path:
                yield item
                continue

            data = {
                key: value
                for key, value in list(item.items())
                if not key.startswith("_")
            }
            if not data:
                yield item
                continue

            files = item.setdefault(fileskey, {})
            files[self.key] = dict(
                name="_content.json",
                data=self.encoder.encode(data),
                contenttype="application/json",
            )

            yield item


@provider(ISectionBlueprint)
@implementer(ISection)
class DeserializerSection:
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = (
            transmogrifier.context if transmogrifier.context else getSite()
        )  # noqa

        self.fileskey = defaultMatcher(options, "files-key", name, "files")
        self.key = options.get("key", "content").strip()

    def __iter__(self):
        for item in self.previous:
            fileskey = self.fileskey(*list(item.keys()))[0]

            files = item.get(fileskey)
            if not files:
                yield item
                continue

            content = files.get(self.key)
            if not content:
                yield item
                continue

            data = json.loads(content["data"])
            item.update(data)

            yield item
