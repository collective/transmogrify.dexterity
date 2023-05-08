"""Installer for the transmogrify.dexterity package."""
from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = f"""
{Path("README.md").read_text()}\n
{Path("CONTRIBUTORS.md").read_text()}\n
{Path("CHANGES.md").read_text()}\n
"""


setup(
    name="transmogrify.dexterity",
    version="3.0.0",
    description="A transmogrifier blueprint for updating dexterity objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
            "zope.testrunner",
            "plone.app.testing",
            "plone.formwidget.contenttree",
            "ftw.builder",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
