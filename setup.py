#!/usr/bin/env python
# Copyright 2007 Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Setup module for python-gflags."""

import sys

try:
  from setuptools import find_packages, setup, Command
except ImportError:
  from distutils.core import find_packages, setup, Command

try:
  from setuptools.commands.bdist_rpm import bdist_rpm
except ImportError:
  from distutils.command.bdist_rpm import bdist_rpm


class BdistRPMCommand(bdist_rpm):
  """Custom handler for the bdist_rpm command."""

  def _make_spec_file(self):
    """Generates the text of an RPM spec file.

    Returns:
      A list of strings containing the lines of text.
    """
    # Note that bdist_rpm can be an old style class.
    if issubclass(BdistRPMCommand, object):
      spec_file = super(BdistRPMCommand, self)._make_spec_file()
    else:
      spec_file = bdist_rpm._make_spec_file(self)

    if sys.version_info[0] < 3:
      python_package = 'python'
    else:
      python_package = 'python3'

    description = []
    name = ''
    summary = ''
    in_description = False

    python_spec_file = []
    for index, line in enumerate(spec_file):
      if line.startswith('%define name '):
        name = line[20:]

      elif line.startswith('Summary: '):
        summary = line

      elif line.startswith('BuildRequires: '):
        line = 'BuildRequires: {0:s}-setuptools'.format(python_package)

      elif line.startswith('Requires: '):
        if python_package == 'python3':
          line = line.replace('python', 'python3')

      elif line.startswith('%description'):
        in_description = True

      elif line.startswith('%files'):
        if python_package == 'python3':
          line = '%files -f INSTALLED_FILES -n {0:s}-{1:s}'.format(
             python_package, name)

      elif line.startswith('%prep'):
        in_description = False

        if python_package == 'python3':
          python_spec_file.append(
              '%package -n {0:s}-{1:s}'.format(python_package, name))
          python_spec_file.append('{0:s}'.format(summary))
          python_spec_file.append('')
          python_spec_file.append(
              '%description -n {0:s}-{1:s}'.format(python_package, name))
          python_spec_file.extend(description)

      elif in_description:
        # Ignore leading white lines in the description.
        if not description and not line:
          continue

        description.append(line)

      python_spec_file.append(line)

    return python_spec_file


setup(name='python-gflags',
      version='3.0.0',
      description='Google Commandline Flags Module',
      license='BSD',
      author='Google Inc. and others',
      author_email='google-gflags@googlegroups.com',
      url='https://github.com/google/python-gflags',
      packages=find_packages('.'),
      py_modules=['gflags'],
      data_files=[('bin', ['gflags2man.py'])],
      include_package_data=True,
      cmdclass={'bdist_rpm': BdistRPMCommand},
     )
