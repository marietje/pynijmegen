#!/usr/bin/env python

from setuptools import setup
from get_git_version import get_git_version

setup(name='pynijmegen',
      version=get_git_version(),
      description='Full-screen status display for MarieD music daemon',
      author='Bas Westerbaan',
      author_email='bas@westerbaan.name',
      url='http://github.com/marietje/pynijmegen/',
      packages=['pynijmegen'],
      package_data={'': ['*.mirte']},
      zip_safe=False,
      package_dir={'pynijmegen': 'src'},
      install_requires = ['docutils>=0.3',
                          'mirte>=0.1.0a2',
                          'sarah>=0.1.0a2',
                          'joyce>=0.1.0a2'],
      )
