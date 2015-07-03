# Copyright (C) 2015 SUSE Linux GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,USA.


import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest


SET_VERSION_EXECUTABLE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../', 'set_version')
)


class SetVersionBaseTest(unittest.TestCase):
    """Basic test class. Other tests should use this one"""

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix='obs-service-set_version-test-')
        os.chdir(self._tmpdir)

    def __file_contains_string(self, file_path, string):
        with open(file_path, "r") as f:
            content = f.read()
        m = re.search(re.escape(string), content)
        return (m is not None, content)

    def _check_file_assert_contains(self, file_path, string):
        contains, content = self.__file_contains_string(file_path, string)
        err_msg = "%s doesn't contain match of %s. " \
                  "Content is:\n#####\n%s#####" % (
                      file_path, string, content)
        self.assertTrue(contains,
                        err_msg)

    def _check_file_assert_not_contains(self, file_path, string):
        contains, content = self.__file_contains_string(file_path, string)
        err_msg = "%s contain match of %s. " \
                  "Content is:\n#####\n%s#####" % (
                      file_path, string, content)
        self.assertFalse(contains,
                         err_msg)

    def _write_tarfile(self, tar_name, tar_dirs):
        """write a tarfile with the given (empty) dirs"""
        tar_path = os.path.join(self._tmpdir, tar_name)
        with tarfile.open(tar_path, "w") as t:
            for d in tar_dirs:
                td = tarfile.TarInfo(d)
                td.type = tarfile.DIRTYPE
                t.addfile(td)
        return tar_path

    def _run_set_version(self, params=[]):
        cmd = [SET_VERSION_EXECUTABLE, '--outdir', '.'] + params
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                "Can not call '%s' in dir '%s'. Error: %s" % ("".join(cmd),
                                                              self._tmpdir,
                                                              e.output))

    def tearDown(self):
        shutil.rmtree(self._tmpdir)
