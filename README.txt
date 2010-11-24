transmogrify.dexterity
======================

The transmogrify.dexterity package provides a dexterity schema updater pipeline section. It updates field values for dexterity content objects.

The dexterityupdater section only needs the path to object, and all fieldname-value pairs in the pipeline (Paths are allways interpreted as relative to the context).

The DexterityUpdateSection works on the following order 
    1. He sets the values from the pipeline (key must be the fieldname)
    2. For all Fields they are empty (None or Missing Value), he try to set a default value, when he exists.

The DexterityUpdateSection can also handle fields in additional behaviors.

actually tested and supported fields
------------------------------------
- TextLine or Text
- Bool
- List
- NamedFileField
    need a dict with data and filename or get the filename in a seperated value      from the pipeline
- Date
    need a datetime.date object or a string in the following format "%d.%m.%Y"
