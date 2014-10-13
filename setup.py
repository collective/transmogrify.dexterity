from setuptools import setup
from setuptools import find_packages


version = open('transmogrify/dexterity/version.txt').read().strip()
maintainer = 'Philippe Gross'
desc = 'A transmogrifier blueprint for updating dexterity objects'
long_desc = open('README.rst').read() + '\n\n' + open('HISTORY.rst').read()
tests_require = [
    'plone.app.testing',
    'plone.app.dexterity',
    'plone.namedfile[blobs]',
    'plone.directives.form',
]


setup(
    name='transmogrify.dexterity',
    version=version,
    description=desc,
    long_description=long_desc,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
