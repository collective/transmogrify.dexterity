# -*- coding: utf-8 -*-
"""Installer for the transmogrify.dexterity package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='transmogrify.dexterity',
    version='1.6.5.dev0',
    description="A transmogrifier blueprint for updating dexterity objects",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='4teamwork AG',
    author_email='info@4teamwork.ch',
    url='https://github.com/collective/transmogrify.dexterity',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/transmogrify.dexterity',
        'Source': 'https://github.com/collective/transmogrify.dexterity',
        'Tracker': 'https://github.com/collective/transmogrify.dexterity/issues',
        # 'Documentation': 'https://transmogrify.dexterity.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['transmogrify'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7",
    install_requires=[
        'collective.transmogrifier',
        'plone.app.textfield',
        'plone.app.transmogrifier',
        'plone.dexterity',
        'plone.namedfile',
        'plone.supermodel',
        'plone.uuid',
        'setuptools',
        'z3c.form',
    ],
    extras_require={
        'test': [
            'ftw.builder',
            'plone.app.dexterity',
            'plone.app.intid',
            'plone.app.testing',
            'plone.directives.form',
            'plone.formwidget.contenttree',
            'plone.namedfile[blobs]',
            'unittest2',
            'z3c.relationfield',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = transmogrify.dexterity.locales.update:update_locale
    """,
)
