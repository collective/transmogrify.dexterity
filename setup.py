from setuptools import setup, find_packages
import os

version = open('transmogrify/dexterity/version.txt').read().strip()
maintainer = 'Philippe Gross'

setup(name='transmogrify.dexterity',
      version=version,
      description="Transmogrifier dexterity updateder section (Maintainer: %s)" % maintainer,
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
        'z3c.form',
        'plone.namedfile',
        'plone.dexterity',
        'collective.transmogrifier',
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
