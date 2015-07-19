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
class SetVersionSpecfile(SetVersionBaseTest):
    """Test set_version service for .spec files"""

    def _write_specfile(self, spec_name, spec_tags, custom=[]):
        """write a given filename with the given rpm tags and custom
        strings (i.e. '%define foo bar')"""
        spec_path = os.path.join(self._tmpdir, spec_name)
        with open(spec_path, "a") as f:
            for c in custom:
                f.write("%s\n" % c)
            for key, val in spec_tags.items():
                f.write("%s: %s\n" % (key, val))
            f.write("\n")
        return spec_path

    @file_data("data_test_from_commandline.json")
    def test_from_commandline(self, data):
        spec_tags, new_version = data
        spec_path = self._write_specfile("test.spec", spec_tags)
        self._run_set_version(params=['--version', new_version])
        self._check_file_assert_contains(spec_path, new_version)

    @file_data("data_test_from_commandline_with_single_file.json")
    def test_from_commandline_with_single_file(self, data):
        spec_tags, new_version, spec_file, other_spec_files = data
        """only a single .spec file should contain the given version"""
        spec_path = self._write_specfile(spec_file, spec_tags)
        # other spec file which shouldn't be updated
        other_spec_path = []
        for s in other_spec_files:
            other_spec_path.append(self._write_specfile(s, spec_tags))
        self._run_set_version(params=["--version", new_version,
                                      "--file", spec_file])
        # our given spec should have the version
        self._check_file_assert_contains(spec_path, new_version)
        # all others shouldn't
        for s in other_spec_path:
            self._check_file_assert_not_contains(s, new_version)

    @file_data("data_test_from_commandline_with_multiple_files.json")
    def test_from_commandline_with_multiple_files(self, data):
        """all .spec files should contain the given version"""
        spec_tags, new_version, spec_files = data
        spec_path = []
        for s in spec_files:
            spec_path.append(self._write_specfile(s, spec_tags))
        self._run_set_version(params=["--version", new_version])
        for s in spec_path:
            self._check_file_assert_contains(s, new_version)

    @file_data("data_test_from_tarball_with_single_file.json")
    def test_from_tarball_with_single_file(self, data):
        tarball_name, tarball_dirs, expected_version = data
        spec_path = self._write_specfile("test.spec",
                                         {"Name": "foo",
                                          "Version": "UNKNOWN",
                                          "Group": "AnyGroup"})
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version()
        self._check_file_assert_contains(spec_path, expected_version)
        self._check_file_assert_contains(spec_path, "Name: foo")
        self._check_file_assert_contains(spec_path, "Group: AnyGroup")

    @file_data("data_test_from_tarball_with_basename_with_multiple_files.json")
    def test_from_tarball_with_basename_with_multiple_files(self, data):
        tarball_name, tarball_dirs, expected_version, spec_files = data
        spec_path = []
        for s in filter(lambda x: x.endswith(".spec"), spec_files):
            spec_path.append(self._write_specfile(s, {"Version": "UNKNOWN"}))
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version(["--basename", "testprog"])
        for s in spec_path:
            self._check_file_assert_contains(s, expected_version)

    @file_data("data_test_from_tarball_with_basename.json")
    def test_from_tarball_with_basename(self, data):
        tarball_name, tarball_dirs, expected_version = data
        spec_path = self._write_specfile("test.spec", {"Version": "UNKNOWN"})
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version(["--basename", "testprog"])
        self._check_file_assert_contains(spec_path, expected_version)
