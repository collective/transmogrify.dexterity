from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from plone.app.multilingual.interfaces import IMutableTG
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFPlone.interfaces import ILanguage
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import provider


@provider(ISectionBlueprint)
@implementer(ISection)
class DexterityTranslationSection:
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = (
            transmogrifier.context if transmogrifier.context else getSite()
        )  # noqa
        self.name = name
        self.pathkey = defaultMatcher(options, "path-key", name, "path")
        self.langkey = options.get("lang-key", "_lang").strip()
        self.tgkey = options.get("tg-key", "_tg").strip()

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

            obj = self.context.unrestrictedTraverse(path.encode().lstrip("/"), None)

            if not IDexterityContent.providedBy(obj):
                # Path doesn't exist
                # obj can not only be None, but also the value of an attribute,
                # which is returned by traversal.
                yield item
                continue

            # fetch lang and translation group
            lang = item.get(self.langkey)
            tg = item.get(self.tgkey)

            # no translation
            if not lang or not tg:
                yield item
                continue

            # set language and translation group
            ILanguage(obj).set_language(lang)
            IMutableTG(obj).set(tg)
            obj.reindexObject()

            yield item
