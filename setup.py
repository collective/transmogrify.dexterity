from setuptools import setup, find_packages
import os

version = open('transmogrify/dexterity/version.txt').read().strip()
maintainer = 'Philippe Gross'

tests_require = [
    'plone.app.testing',
    'plone.app.dexterity',
    'plone.namedfile[blobs]',
]
setup(name='transmogrify.dexterity',
      version=version,
      description="A transmogrifier blueprint for updating dexterity objects",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
