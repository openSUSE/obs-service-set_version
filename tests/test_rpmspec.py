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
import tarfile

from ddt import data, ddt, unpack

from test_base import SetVersionBaseTest


@ddt
class SetVersionSpecfile(SetVersionBaseTest):
    """Test set_version service for .spec files"""

    def _write_specfile(self, spec_name, spec_tags):
        """write a given filename with the given rpm tags"""
        spec_path = os.path.join(self._tmpdir, spec_name)
        with open(spec_path, "a") as f:
            for key, val in spec_tags.items():
                f.write("%s: %s" % (key, val))
            f.write("\n")
        return spec_path

    def _write_tarfile(self, tar_name, tar_dirs):
        """write a tarfile with the given (empty) dirs"""
        tar_path = os.path.join(self._tmpdir, tar_name)
        with tarfile.open(tar_path, "w") as t:
            for d in tar_dirs:
                td = tarfile.TarInfo(d)
                td.type = tarfile.DIRTYPE
                t.addfile(td)
        return tar_path

    @data(
        ({"Version": "1.2.3"}, "1"),
        ({"Version": "1.2.3"}, "3.4.5"),
        ({"Version": "1.2.3~456+789-Devel3"}, "3.4.5"),
        ({"Version": "3.4.5"}, "1.2.3~456+789-Devel3"),
    )
    @unpack
    def test_from_commandline(self, spec_tags, new_version):
        spec_path = self._write_specfile("test.spec", spec_tags)
        self._run_set_version(params=['--version', new_version])
        self._check_file_assert_contains(spec_path, new_version)

    @data(
        ({"Version": "4.5.6"}, "1",
         "test1.spec", ["test2.spec"]),
        ({"Version": "1.2.3"}, "3.4.5",
         "test1.spec", ["test2.spec"]),
        ({"Version": "1.2.3~456+789-Devel3"}, "3.4.5",
         "test1.spec", ["test2.spec"]),
        ({"Version": "3.4.5"}, "1.2.3~456+789-Devel3",
         "test1.spec", ["test2.spec"]),
    )
    @unpack
    def test_from_commandline_with_single_file(self, spec_tags,
                                               new_version, spec_file,
                                               other_spec_files):
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

    @data(
        ({"Version": "4.5.6"}, "1",
         ["test1.spec", "test2.spec"]),
    )
    @unpack
    def test_from_commandline_with_multiple_files(self, spec_tags,
                                                  new_version, spec_files):
        """all .spec files should contain the given version"""
        spec_path = []
        for s in spec_files:
            spec_path.append(self._write_specfile(s, spec_tags))
        self._run_set_version(params=["--version", new_version])
        for s in spec_path:
            self._check_file_assert_contains(s, new_version)

    @data(
        ("testprog-1.2.3.tar", [], "1.2.3"),
        ("tetsprog-2015.10.tar", [], "2015.10"),
        ("testprog-512.tar", [], "512"),
        ("1.2.3.tar", ["testprog-4.5.6"], "4.5.6"),
        ("testprog-1.2.3.tar", ["testprog-4.5.6"], "1.2.3"),
        ("testprog-master.tar", ["testprog-4.5.6"], "4.5.6"),
        )
    @unpack
    def test_from_tarball_with_single_file(self, tarball_name,
                                           tarball_dirs,
                                           expected_version):
        spec_path = self._write_specfile("test.spec", {"Version": "UNKNOWN"})
        self._write_tarfile(tarball_name, tarball_dirs)
        self._run_set_version()
        self._check_file_assert_contains(spec_path, expected_version)

    @data(
        ("testprog-1.2.3.tar", [],
         "1.2.3", ["test1.spec", "test2.spec"]),
        ("testprog-1.2.3.tar", ["xyz-4.5.6"],
         "1.2.3", ["test1.spec", "test2.spec"]),
        ("helloworld-1.2.3.tar", ["testprog-4.5.6"],
         "4.5.6", ["test1.spec", "test2.spec"]),
        ("helloworld-1.2.3.tar", ["testprog-4.5.6", "another-testprog-7"],
         "4.5.6", ["test1.spec", "test2.spec"]),
        )
    @unpack
    def test_from_tarball_with_basename_with_multiple_files(
            self, tarball_name, tarball_dirs, expected_version, spec_files):
        spec_path = []
        for s in spec_files:
            spec_path.append(self._write_specfile(s, {"Version": "UNKNOWN"}))
        self._write_tarfile(tarball_name, tarball_dirs)
        self._run_set_version(["--basename", "testprog"])
        for s in spec_path:
            self._check_file_assert_contains(s, expected_version)

    @data(
        ("testprog-1.2.3.tar", [], "1.2.3"),
        ("testprog-1.2.3.tar", ["xyz-4.5.6"], "1.2.3"),
        ("helloworld-1.2.3.tar", ["testprog-4.5.6"], "4.5.6"),
        ("helloworld-1.2.3.tar", ["testprog-4.5.6", "another-testprog-7"],
         "4.5.6"),
        )
    @unpack
    def test_from_tarball_with_basename(self, tarball_name,
                                        tarball_dirs,
                                        expected_version):
        spec_path = self._write_specfile("test.spec", {"Version": "UNKNOWN"})
        self._write_tarfile(tarball_name, tarball_dirs)
        self._run_set_version(["--basename", "testprog"])
        self._check_file_assert_contains(spec_path, expected_version)
