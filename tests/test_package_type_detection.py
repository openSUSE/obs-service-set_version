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


import imp

from ddt import data, ddt, unpack

from test_base import SetVersionBaseTest


# NOTE(toabctl): Hack to import non-module file for testing
sv = imp.load_source("set_version", "set_version")


@ddt
class PackageTypeDetector(SetVersionBaseTest):
    @data(
        ("test.tar", [], ["test.egg-info/PKG-INFO"], "python"),
        ("test.tar", [], ["test-1.2.3a1/test.egg-info/PKG-INFO"], "python"),
        ("test.tar", [], ["PKG-INFO"], None),
        ("test.tar", [], ["foo.py"], None)
    )
    @unpack
    def test_detection(self, tar_name, tar_dirs, tar_files, expected_result):
        self._write_tarfile(tar_name, tar_dirs, tar_files)
        files = sv._get_local_files()
        pack_type = sv.PackageTypeDetector._get_package_type(files)
        self.assertEqual(expected_result, pack_type)
