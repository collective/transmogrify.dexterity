from setuptools import setup
from setuptools import find_packages

version = '1.6.0'
maintainer = 'Philippe Gross'
desc = 'A transmogrifier blueprint for updating dexterity objects'
long_desc = open('README.rst').read() + '\n\n' + open('CHANGES.rst').read()
tests_require = [
    'ftw.builder',
    'plone.app.intid',
    'plone.app.testing',
    'plone.app.dexterity',
    'plone.namedfile[blobs]',
    'plone.directives.form',
    'plone.formwidget.contenttree',
    'z3c.relationfield',
]


setup(
    name='transmogrify.dexterity',
    version=version,
    description=desc,
    long_description=long_desc,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='',
    author='%s, 4teamwork GmbH' % maintainer,
    author_email='mailto:info@4teamwork.ch',
    maintainer=maintainer,
    url='http://psc.4teamwork.ch/dist/transmogrify.dexterity',
    license='GPL2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['transmogrify'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.transmogrifier',
        'plone.app.textfield',
        'plone.app.transmogrifier',
        'plone.dexterity',
        'plone.namedfile',
        'plone.supermodel',
        'plone.uuid',
        'z3c.form',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
