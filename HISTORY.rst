Changelog
=========


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
