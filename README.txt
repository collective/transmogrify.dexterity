Introduction
============

The transmogrify.dexterity package provides a transmogrifier pipeline section
for updating field values of dexterity content objects. The blueprint name is ``transmogrify.dexterity.schemaupdater``. 

The schemaupdater section needs at least the path to the object to update.
Paths to objects are always interpreted as being relative to the context. Any
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
    needs a dict with data and filename or get the filename in a seperated value from the pipeline
- Date
    needs a datetime.date or datetime.datetime object, or a string in the following format "%Y-%m-%d"


Default pipelines
=================

This package also registers a number of pipelines for you to use. To add them
to a GenericSetup profile, create a ``transmogrifier.txt`` with the name of the
pipeline you wish to use.

transmogrify.dexterity.csvimport
--------------------------------

This pipeline will convert a CSV file into dexterity content. By default, the
CSV file will be found in ``/tmp/entries.csv``.

NB: Unfortunately it cannot read files out of GS profiles, this is a limitation
in the csvsource, one I may well fix.

Any column beyond the ones listed below will be presumed to be a Dexterity
field, and will be updated. Special columns are:

- _type
    portal_type of content (optional, default is Document)
- _path
    Full path to content item, including content item.
- _folder
    Folder containing item, id will be derived from title
- _transitions
    Workflow transition (optional, default is "publish")

TODO
----
- General support for all fields
- Tests
