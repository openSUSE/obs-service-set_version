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
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest


from ddt import data, ddt, unpack


# NOTE(toabctl): Hack to import non-module file for testing
sv = imp.load_source("set_version", "set_version")


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

    def _write_tarfile(self, tar_name, tar_dirs, tar_files):
        """write a tarfile with the given dirs and given files"""
        tar_path = os.path.join(self._tmpdir, tar_name)
        with tarfile.open(tar_path, "w") as t:
            for d in tar_dirs:
                td = tarfile.TarInfo(d)
                td.type = tarfile.DIRTYPE
                t.addfile(td)
            for f in tar_files:
                td = tarfile.TarInfo(f)
                t.addfile(td)
        return tar_path

    def _run_set_version(self, params=[]):
        self._tmpoutdir = tempfile.mkdtemp(
            prefix='obs-service-set_version-test-outdir-')
        cmd = [sys.executable,
               SET_VERSION_EXECUTABLE,
               '--outdir', self._tmpoutdir] + params
        try:
            subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, env=os.environ.copy())
            for f in os.listdir(self._tmpoutdir):
                os.unlink(self._tmpdir+"/"+f)
                # FIXME: in most modes the files get not replaced,
                # but store in parallel with _service: prefix
                shutil.move(self._tmpoutdir+"/"+f, self._tmpdir)
            shutil.rmtree(self._tmpoutdir)
        except subprocess.CalledProcessError as e:
            raise Exception(
                "Can not call '%s' in dir '%s'. Error: %s" % ("".join(cmd),
                                                              self._tmpdir,
                                                              e.output))

    def tearDown(self):
        shutil.rmtree(self._tmpdir)


@ddt
class TestSetVersionBasics(SetVersionBaseTest):
    @data(
        (
            ["%define version_unconverted 1.2.3"],
            ["%define version_unconverted 4.5.6"],
            "version_unconverted", "4.5.6"
        ),
        (
            ["%define version_unconverted     1.2.3"],
            ["%define version_unconverted     4.5.6"],
            "version_unconverted", "4.5.6"
        ),
        (
            ["Hi foo", "%define version_unconverted 1.2.3", "Ho bar"],
            ["Hi foo", "%define version_unconverted 4.5.6", "Ho bar"],
            "version_unconverted", "4.5.6"
        ),
        (
            [
                "%define foodef bar",
                "%define version_unconverted 1.2.3",
                "%define bardef foo"
            ],
            [
                "%define foodef bar",
                "%define version_unconverted 4.5.6",
                "%define bardef foo"
            ],
            "version_unconverted", "4.5.6"
        )
    )
    @unpack
    def test_replace_define_replace(self, lines, expected_lines,
                                    define_name, define_value):
        fn = os.path.join(self._tmpdir, "test-file")
        with open(fn, "w") as f:
            f.write("\n".join(lines))
        # do the replacement
        sv._replace_define(os.path.basename(fn),
                           define_name, define_value)
        # check
        with open(fn, "r") as f:
            current_lines = f.read().split("\n")
            self.assertEqual(len(current_lines), len(expected_lines))
            for nbr, l in enumerate(current_lines):
                self.assertEqual(l, expected_lines[nbr])

    @data(
        (
            ["Name: foobar"],
            ["%define version_unconverted 4.5.6", "", "Name: foobar"],
            "version_unconverted", "4.5.6"
        ),
        (
            ["Name: foobar"],
            ["%define version_unconverted 4.5.6", "", "Name: foobar"],
            "version_unconverted", "4.5.6"
        ),
        (
            ["AnyTag: ha", "Name: foo"],
            [
                "AnyTag: ha",
                "%define version_unconverted 4.5.6",
                "",
                "Name: foo"
            ],
            "version_unconverted", "4.5.6"
        ),
        (
            ["Name: foobar", "Version: 1.2.3"],
            [
                "%define version_unconverted 4.5.6",
                "",
                "Name: foobar",
                "Version: 1.2.3"
            ],
            "version_unconverted", "4.5.6"
        )
    )
    @unpack
    def test_replace_define_add(self, lines, expected_lines,
                                define_name, define_value):
        fn = os.path.join(self._tmpdir, "test-file")
        with open(fn, "w") as f:
            f.write("\n".join(lines))
        # do the addition
        sv._replace_define(os.path.basename(fn),
                           define_name, define_value)
        # check
        with open(fn, "r") as f:
            current_lines = f.read().split("\n")
            self.assertEqual(len(current_lines), len(expected_lines))
            for nbr, l in enumerate(current_lines):
                self.assertEqual(l, expected_lines[nbr])

    @data(
        (
            ["%setup -q -n %{component}-%{version}"],
            ["%setup -q -n %{component}-%{version_unconverted}"],
        ),
        (
            ["%setup -q -n %{component}-1.2.3"],
            ["%setup -q -n %{component}-1.2.3"],
        ),
        (
            ["%setup -q -n foobar-%{version}"],
            ["%setup -q -n foobar-%{version_unconverted}"],
        ),
        (
            ["%setup -q -n foobar-%{version}-bar"],
            ["%setup -q -n foobar-%{version_unconverted}-bar"],
        ),
        (
            ["foo", "%setup -q -n %{component}-%{version}", "bar"],
            ["foo", "%setup -q -n %{component}-%{version_unconverted}", "bar"],
        ),
        (
            ["foo", "%setup -q -n %{component}-%{version}", "bar"],
            ["foo", "%setup -q -n %{component}-%{version_unconverted}", "bar"],
        ),
        (
            ["foo", "%setup -q", "bar"],
            ["foo", "%setup -q -n %{name}-%{version_unconverted}", "bar"],
        ),
        (
            ["foo", "%setup", "bar"],
            ["foo", "%setup  -n %{name}-%{version_unconverted}", "bar"],
        )
    )
    @unpack
    def test_replace_spec_setup(self, lines, expected_lines):
        fn = os.path.join(self._tmpdir, "test-file")
        with open(fn, "w") as f:
            f.write("\n".join(lines))
        # do the replacement
        sv._replace_spec_setup(os.path.basename(fn), "version_unconverted")
        # check
        with open(fn, "r") as f:
            current_lines = f.read().split("\n")
            self.assertEqual(len(current_lines), len(expected_lines))
            for nbr, l in enumerate(current_lines):
                self.assertEqual(l, expected_lines[nbr])

    def test_autodetect_filename(self):
        dname = os.path.join(self._tmpdir, "test-v1.2.3")
        os.chdir(self._tmpdir)
        os.mkdir(dname)
        subprocess.call(['tar', '-cf', 'test-v1.2.3.tar', 'test-v1.2.3'])
        files_local = ['test-v1.2.3.tar']

        # checking dirname in archive detection
        args = {'regex': '^test-v(.*)', 'basename': ''}
        ver = sv._version_detect(args, files_local)
        self.assertEqual(ver, '1.2.3')

        # checking archive filename detection
        args = {'regex': '^test-v(.*).tar', 'basename': ''}
        ver = sv._version_detect(args, files_local)
        self.assertEqual(ver, '1.2.3')
