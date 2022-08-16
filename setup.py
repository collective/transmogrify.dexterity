"""Installer for the transmogrify.dexterity package."""
from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="transmogrify.dexterity",
    version="3.0.0.dev0",
    description="A transmogrifier blueprint for updating dexterity objects",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="4teamwork AG",
    author_email="info@4teamwork.ch",
    url="https://github.com/collective/transmogrify.dexterity",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/transmogrify.dexterity",
        "Source": "https://github.com/collective/transmogrify.dexterity",
        "Tracker": "https://github.com/collective/transmogrify.dexterity/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["transmogrify"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "collective.transmogrifier",
        "plone.app.transmogrifier",
        "Products.CMFPlone",
        "setuptools",
    ],
    extras_require={
        "test": [
            "zest.releaser[recommended]",
            "zope.testrunner",
            "plone.app.testing>=7.0.0a3",
            "plone.formwidget.contenttree",
            "ftw.builder",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
