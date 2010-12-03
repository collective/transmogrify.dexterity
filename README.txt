Introduction
============

The transmogrify.dexterity package provides a transmogrifier pipeline section
for updating field values of dexterity content objects. The blueprint name is ``transmogrify.dexterity.schemaupdater``. 

The schemaupdater section needs at least the path to object to update.
Paths to objects are always interpreted as relative to the context. Any
writable field who's id matches a key in the current item will be updated with
the corresponding value.

Fields that do not get a value from the pipeline are initialized with their
default value or get a missing_value marker.
This functionality will be moved into a separate constructor pipeline...

The schmemaupdater section can also handle fields defined in behaviors.


Actually tested and supported fields
------------------------------------
- TextLine or Text
- Bool
- List
- NamedFileField
    need a dict with data and filename or get the filename in a seperated value from the pipeline
- Date
    need a datetime.date object or a string in the following format "%d.%m.%Y"

TODO
----
- Generally support for all fields
- Tests


