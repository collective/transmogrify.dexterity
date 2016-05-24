Changelog
=========


1.6.2 (2016-05-24)
------------------

- Fix blueprint context for support with ``transmogrifier`` package (not ``collective.transmogrifier``), which does not have dependencies to CMFPlone and thus doesn't provide a useful context.
  [thet]


1.6.1 (2015-09-30)
------------------

- Do not import from deprecated zope.app.intid anymore, use zope.intid instead
  [jensens]

- Fix deserializer if datetime is string "None".
  [elioschmutz]


1.6.0 (2015-08-28)
------------------

- Implement new deserializer for datetime fields.
  [mbaechtold]


1.5.2 (2015-07-13)
------------------

- Fix default container description to be unicode, not bytestring.
  See https://github.com/plone/plone.dexterity/pull/33
  [jone]


1.5.1 (2015-05-27)
------------------

- Make z3c.relationfield imports conditional.
  [jone]


1.5 (2015-05-26)
----------------

- When retrieving the object via traversal from the path, check if it provides
  IDexterityContent. Traversal can also return attributes of objects, if no
  object can be found but the path element is named like an attribute.
  [thet]

- Handle collective.jsonify structures, specifically _datafield_FIELDNAME and
  _content_type_FIELDNAME keys.
  [thet]

- PEP8.
  [thet]

- Add value converters for z3c.relationfield relation(-lists).
  [deiferni]


1.4 (2014-11-06)
----------------

- Add blueprint for managing plone.app.multilingual translations
  [rnix]


1.3 (2014-07-25)
----------------

- Use zope.dottedname.resolve to find class
  [lentinj]

- Serialize/Deserialize zope.schema.IObjects
  [lentinj]

- Add 'logger' and 'loglevel' options so invalid fields are logged when
  disable-constraints is True
  [ebrehault]


1.2 (2013-08-29)
----------------

- Only update with a default value if there isn't a value already set
  on the field. (NB: before a default value would be set, regardless
  of the current field value).
  [lentinj]


1.1 (2013-07-23)
----------------

- Don't try to write readonly fields
  [djowett]

- Added in a generic CSV -> content pipeline
  [lentinj]


1.0 (2011-11-17)
----------------

- Updated changelog to be zest releaser compatible
  [lgraf]


1.0a5 (2011-07-18)
------------------

- Added check-constraints option to schemaupdater section.
  If set to False, field values that are set in the schemaupdater section won't
  be validated against the field's constraints.
  [lgraf]

- Made CollectionDeserializer cast None and empty string to an empty list
  [lgraf]

- Added a basic DateDeserializer
  [lgraf]

- Using new-style classes for [de]serializers
  [lgraf]


1.0a4 (2011-06-07)
------------------

- Ensure RichTextValue gets a decoded unicode string, add tests
  [lentinj]

- Refactor to support more field types.
  [elro]


1.0a3 (2010-03-12)
------------------

- Fixed bug in typechecking of values for Boolean fields
  [lgraf]

- fixed dateconverting
  [phgross]

- fixed value check: so that it works correctly with an empty string
  [phgross]

- fixed handling for list and bool fields
  [phgross]
