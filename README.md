<h1 align="center">transmogrify.dexterity</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)
[![PyPI - License](https://img.shields.io/pypi/l/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)
[![PyPI - Status](https://img.shields.io/pypi/status/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/transmogrify.dexterity)](https://pypi.org/project/transmogrify.dexterity/)

[![Code analysis checks](https://github.com/collective/transmogrify.dexterity/actions/workflows/code-analysis.yml/badge.svg)](https://github.com/collective/transmogrify.dexterity/actions/workflows/code-analysis.yml)
[![Tests](https://github.com/collective/transmogrify.dexterity/actions/workflows/tests.yml/badge.svg)](https://github.com/collective/transmogrify.dexterity/actions/workflows/tests.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/transmogrify.dexterity)](https://github.com/collective/transmogrify.dexterity)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/transmogrify.dexterity?style=social)](https://github.com/collective/transmogrify.dexterity)

</div>

## Introduction

The transmogrify.dexterity package provides a transmogrifier pipeline section
for updating field values of dexterity content objects. The blueprint name is
`transmogrify.dexterity.schemaupdater`.

The schemaupdater section needs at least the path to the object to update.
Paths to objects are always interpreted as being relative to the context. Any
writable field who's id matches a key in the current item will be updated with
the corresponding value.

Fields that do not get a value from the pipeline are initialized with their
default value or get a missing_value marker.
This functionality will be moved into a separate constructor pipeline...

The schmemaupdater section can also handle fields defined in behaviors.


## Actually tested and supported fields

- TextLine or Text

- Bool

- List

- NamedFileField: needs a dict with data and filename or get the filename in a seperated value from the pipeline

- Date:"needs a datetime.date or datetime.datetime object, or a string in the following format "%Y-%m-%d"

- Datetime: needs a datetime.datetime object, or a string parseable by    `DateTime.DateTime` e.g. "2015-12-31 17:59:59" or "2004/12/30 00:20:00 GMT+1" etc.


## Default pipelines

This package also registers a number of pipelines for you to use. To add them
to a GenericSetup profile, create a `transmogrifier.txt` with the name of the
pipeline you wish to use.


### transmogrify.dexterity.csvimport

This pipeline will convert a CSV file into dexterity content. To use it:

* Name your CSV `entries.csv`

* Create a file called `transmogrifier.txt` with the one line `transmogrify.dexterity.csvimport`

* Add both to a `.tar.gz` file

* Visit /Plone/portal_setup/manage_importSteps

* Select the tarball you just made

* "Import uploaded tarball"

...or add it as part of another GS profile.

The first row of the CSV is presumed to be column headings. Unless a special
column, the column will be presumed to be a dexterity property to update on the
type. Special column names are:-

- _type
    portal_type of content (optional, default is Document)

- _path
    Full path to content item, including content item.

- _folder
    Folder containing item, id will be derived from title

- _transitions
    Workflow transition (optional, default is "publish")

## Developing this package

Create the virtual enviroment and install all dependencies:

```shell
make build
```

Start Plone in foreground:

```shell
make start
```


### Running tests

```shell
make tests
```


### Formatting the codebase

```shell
make format
```

### Linting the codebase

```shell
make lint
```

## License

The project is licensed under the GPLv2.
