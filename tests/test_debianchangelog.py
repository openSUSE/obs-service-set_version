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
import subprocess
import unittest


from ddt import ddt, file_data

from test_base import SetVersionBaseTest


def has_dch_executable():
    """the devscripts package is needed to be able to use 'dch'"""
    with open(os.devnull, "wb") as devnull:
        try:
            subprocess.check_call("dch --version",
                                  stdout=devnull, stderr=devnull, shell=True)
        except subprocess.CalledProcessError:
            return False
        else:
            return True


@ddt
@unittest.skipUnless(has_dch_executable(), "'dch' executable not available")
class SetVersionDebianChangelog(SetVersionBaseTest):
    """Test set_version service for debian/changelog files"""

    def _write_debian_changelog(self, filename, version):
        subprocess.check_call("dch --create --empty -v "
                              "%s --package foobar -c %s" %
                              (version, filename), shell=True)
        return os.path.join(self._tmpdir, filename)

    @file_data("data_test_from_commandline.json")
    def test_from_commandline(self, data):
        old_version, new_version = data
        changelog_path = self._write_debian_changelog(
            "debian.changelog", old_version)
        self._run_set_version(params=['--version', new_version])
        self._check_file_assert_contains(changelog_path, new_version)
        self._check_file_assert_not_contains(changelog_path, old_version)

    @file_data("data_test_from_tarball_with_single_file.json")
    def test_from_tarball_with_single_file(self, data):
        tarball_name, tarball_dirs, old_version, expected_version = data
        changelog_path = self._write_debian_changelog(
            "debian.changelog", old_version)
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version()
        self._check_file_assert_contains(changelog_path, expected_version)
        self._check_file_assert_not_contains(changelog_path, old_version)

    @file_data("data_test_from_tarball_with_basename_with_multiple_files.json")
    def test_from_tarball_with_basename_with_multiple_files(self, data):
        tarball_name, tarball_dirs, expected_version, dchlog_files = data
        dchlog_path = []
        old_version = "9.9.9-1foobar3"
        for s in filter(lambda x: x.endswith("debian.changelog"),
                        dchlog_files):
            dchlog_path.append(
                self._write_debian_changelog(s, old_version))
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version(["--basename", "testprog"])
        for s in dchlog_path:
            self._check_file_assert_contains(s, expected_version)
            self._check_file_assert_not_contains(s, old_version)

    @file_data("data_test_from_tarball_with_basename.json")
    def test_from_tarball_with_basename(self, data):
        tarball_name, tarball_dirs, expected_version = data
        old_version = "9.9.9-0+git3~10"
        dchlog_path = self._write_debian_changelog("debian.changelog",
                                                   old_version)
        self._write_tarfile(tarball_name, tarball_dirs, [])
        self._run_set_version(["--basename", "testprog"])
        self._check_file_assert_contains(dchlog_path, expected_version)
        self._check_file_assert_not_contains(dchlog_path, old_version)
