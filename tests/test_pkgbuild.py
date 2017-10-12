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

from ddt import ddt, file_data

from test_base import SetVersionBaseTest


@ddt
class SetVersionPKGBUILD(SetVersionBaseTest):
    """Test set_version service for PKGBUILD files"""

    def _write_pkgbuild_file(self, pkgbuild_name, tags, custom=[]):
        """write a given filename with the given tags and custom
        strings"""
        pkgbuild_path = os.path.join(self._tmpdir, pkgbuild_name)
        with open(pkgbuild_path, "a") as f:
            for c in custom:
                f.write("%s\n" % c)
            for key, val in tags.items():
                f.write("%s=%s\n" % (key, val))
            f.write("\n")
        return pkgbuild_path

    @file_data("data_test_from_commandline.json")
    def test_from_commandline(self, data):
        old_version, new_version = data
        pkgbuild_path = self._write_pkgbuild_file(
            "PKGBUILD", {"pkgver": old_version, "md5sums": "fail", "sha256sums": "fail"})
        self._run_set_version(params=['--version', new_version])
        expected_str = "pkgver=%s" % (new_version)
        self._check_file_assert_contains(pkgbuild_path, expected_str)
        self._check_file_assert_not_contains(pkgbuild_path, old_version)
        expected_str = "md5sums=('SKIP')"
        self._check_file_assert_contains(pkgbuild_path, expected_str)
        expected_str = "sha256sums=('SKIP')"
        self._check_file_assert_contains(pkgbuild_path, expected_str)
