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

from ddt import data, ddt, unpack

from packaging.version import parse

from test_base import SetVersionBaseTest
from tests.loader import import_set_version


sv = import_set_version()


def _has_zypper():
    with open(os.devnull, 'w') as dn:
        ret = subprocess.call("which zypper",
                              stdout=dn, stderr=subprocess.STDOUT,
                              shell=True)
        if int(ret) == 0:
            return True
        return False


def _has_dpkg():
    with open(os.devnull, 'w') as dn:
        ret = subprocess.call("which dpkg",
                              stdout=dn, stderr=subprocess.STDOUT,
                              shell=True)
        if int(ret) == 0:
            return True
        return False


def _has_packaging():
    try:
        import packaging.version  # noqa: F401
    except ImportError:
        return False
    return True


HAS_ZYPPER = _has_zypper()
HAS_DPKG = _has_dpkg()
HAS_PACKAGING = _has_packaging()


class VersionCompareBase(object):
    def __init__(self, version):
        self.version_str = version

    def __repr__(self):
        return self.version_str


class ZypperVersionCompare(VersionCompareBase):
    """ class to compare version strings with zypper"""
    def _do_compare(self, other):
        # zypper's return val is negative if v1 is older than v2.
        # See 'man zypper'
        ret = subprocess.check_output("zypper --terse versioncmp %s %s" % (
            self.version_str, other.version_str), shell=True)
        return int(ret)

    def __lt__(self, other):
        return self._do_compare(other) < 0

    def __gt__(self, other):
        return self._do_compare(other) > 0

    def __eq__(self, other):
        return (self._do_compare(other) == 0)


class DpkgVersionCompare(VersionCompareBase):
    def __do_compare(self, other, op):
        cmd = 'dpkg --compare-versions "%s" "%s" "%s"' % (
            self.version_str, op, other.version_str)
        ret = subprocess.call(cmd, shell=True)
        if int(ret) == 0:
            return True
        return False

    def __lt__(self, other):
        return self.__do_compare(other, 'lt')

    def __le__(self, other):
        return self.__do_compare(other, 'le')

    def __eq__(self, other):
        return self.__do_compare(other, 'eq')

    def __gt__(self, other):
        return self.__do_compare(other, 'gt')

    def __ge__(self, other):
        return self.__do_compare(other, 'ge')


@ddt
class VersionConverterTest(SetVersionBaseTest):
    @data(
        ('1', '1'),
        ('1.0', '1.0'),
        ('1.0.1', '1.0.1'),
        ('5.0.0.0a1.dev13', '5.0.0.0~xalpha1~dev13'),
        ('2015.2.b123', '2015.2~xbeta123'),
        ('1.2-dev2', '1.2~dev2'),
        ('1.0.post1', '1.0.post1'),
        ('1.0rc1', '1.0~xrc1'),
        ('1.0b1', '1.0~xbeta1'),
        ('1.7.40~svn', ('1.7.40~svn' if not HAS_PACKAGING else None))
    )
    @unpack
    def test_python_version_pip2rpm(self, pip_ver, expected_ver):
        """ See https://www.python.org/dev/peps/pep-0440/\
        #examples-of-compliant-version-schemes """
        rpm_ver = sv._version_python_pip2rpm(pip_ver)
        self.assertEqual(rpm_ver, expected_ver)


@ddt
@unittest.skipIf(HAS_ZYPPER is False and HAS_DPKG is False,
                 "zypper and dpkg are both unavailable")
class VersionCompareTests(SetVersionBaseTest):
    def _do_version_compare(self, v1, op, v2):
        """ make sure that a version compare with pip and
        zypper leads to the same result"""
        # parse pip versions
        v1_pip = parse(v1)
        v2_pip = parse(v2)
        # generate rpm version strings
        v1_rpm = sv._version_python_pip2rpm(v1)
        v2_rpm = sv._version_python_pip2rpm(v2)
        checked_package_managers = [('pip', v1_pip, v2_pip)]
        # generate Zypper objects to be able to compare the strings
        if HAS_ZYPPER:
            v1_zypp = ZypperVersionCompare(v1_rpm)
            v2_zypp = ZypperVersionCompare(v2_rpm)
            checked_package_managers.append(('zypper', v1_zypp, v2_zypp))
        # generate dpkg objects to be able to compare the strings
        if HAS_DPKG:
            v1_dpkg = DpkgVersionCompare(v1_rpm)
            v2_dpkg = DpkgVersionCompare(v2_rpm)
            checked_package_managers.append(('dpkg', v1_dpkg, v2_dpkg))
        # compare version strings for pip, zypper and dpkg
        for type_, vv1, vv2 in checked_package_managers:
            if op == '==':
                self.assertEqual(vv1, vv2,
                                 "%s: %s == %s" % (type_, vv1, vv2))
            elif op == '>':
                self.assertGreater(vv1, vv2,
                                   "%s: %s > %s" % (type_, vv1, vv2))
            elif op == '>=':
                self.assertGreaterEqual(vv1, vv2,
                                        "%s: %s >= %s" % (type_, vv1, vv2))
            elif op == '<':
                self.assertLess(vv1, vv2,
                                "%s: %s < %s" % (type_, vv1, vv2))
            elif op == '<=':
                self.assertLessEqual(vv1, vv2,
                                     "%s: %s <= %s" % (type_, vv1, vv2))
            else:
                raise Exception("Unknown operator '%s'" % op)

    @data(
        # pre release spelling
        # https://www.python.org/dev/peps/pep-0440/#pre-release-spelling
        (
            [
                '1.1a', '1.1-a', '1.1.a', '1.1_a',
                '1.1A', '1.1-A', '1.1.A', '1.1_A',
                '1.1a0', '1.1-a0', '1.1.a0', '1.1_a0',
                '1.1A0', '1.1-A0', '1.1.A0', '1.1_A0',
                '1.1alpha', '1.1-alpha', '1.1.alpha', '1.1_alpha',
                '1.1ALPHA', '1.1-ALPHA', '1.1.ALPHA', '1.1_ALPHA',
                '1.1alpha0', '1.1-alpha0', '1.1.alpha0', '1.1_alpha0',
                '1.1ALPHA0', '1.1-ALPHA0', '1.1.ALPHA0', '1.1_ALPHA0'],
            '==',
            '1.1a0'
        ),
        (
            [
                '1.1b', '1.1-b', '1.1.b', '1.1_b',
                '1.1B', '1.1-B', '1.1.B', '1.1_B',
                '1.1b0', '1.1-b0', '1.1.b0', '1.1_b0',
                '1.1B0', '1.1-B0', '1.1.B0', '1.1_B0',
                '1.1beta', '1.1-beta', '1.1.beta', '1.1_beta',
                '1.1BETA', '1.1-BETA', '1.1.BETA', '1.1_BETA',
                '1.1beta0', '1.1-beta0', '1.1.beta0', '1.1_beta0',
                '1.1BETA0', '1.1-BETA0', '1.1.BETA0', '1.1_BETA0'],
            '==',
            '1.1b0'
        ),
        (
            [
                '1.1c', '1.1-c', '1.1.c', '1.1_c',
                '1.1C', '1.1-C', '1.1.C', '1.1_C',
                '1.1c0', '1.1-c0', '1.1.c0', '1.1_c0',
                '1.1C0', '1.1-C0', '1.1.C0', '1.1_C0',
                '1.1rc', '1.1-rc', '1.1.rc', '1.1_rc',
                '1.1RC', '1.1-RC', '1.1.RC', '1.1_RC',
                '1.1rc0', '1.1-rc0', '1.1.rc0', '1.1_rc0',
                '1.1RC0', '1.1-RC0', '1.1.RC0', '1.1_RC0',
                '1.1pre', '1.1-pre', '1.1.pre', '1.1_pre',
                '1.1PRE', '1.1-PRE', '1.1.PRE', '1.1_PRE',
                '1.1pre0', '1.1-pre0', '1.1.pre0', '1.1_pre0',
                '1.1PRE0', '1.1-PRE0', '1.1.PRE0', '1.1_PRE0',
                '1.1preview', '1.1-preview', '1.1.preview', '1.1_preview',
                '1.1PREVIEW', '1.1-PREVIEW', '1.1.PREVIEW', '1.1_PREVIEW',
                '1.1preview0', '1.1-preview0', '1.1.preview0', '1.1_preview0',
                '1.1PREVIEW0', '1.1-PREVIEW0', '1.1.PREVIEW0', '1.1_PREVIEW0',
            ],
            '==',
            '1.1rc0'
        ),
    )
    @unpack
    def test_version_normalization(self, v1_list, op, v2):
        """ test packaging's version normalization. There are crazy thinks
        like foo-1.0rc0.post1.dev5 possible"""
        # do the tests with and without 'post' releases
        # FIXME(toabctl): See https://github.com/pypa/packaging/issues/35
        # for post releases, also check 'r', 'R', 'ref' and 'REF'
        for p in ['',
                  'post', '-post', '.post', '_post',
                  'post0', '-post0', '.post0', '_post0']:
            # do the tests with and without 'dev' releases
            for d in ['',
                      'dev', '-dev', '.dev', '_dev',
                      'dev0', '-dev0', '.dev0', '_dev0']:
                for vv1 in v1_list:
                    self._do_version_compare("%s%s%s" % (vv1, p, d),
                                             op,
                                             "%s%s%s" % (v2, p, d))

    @data(
        (
            [
                '1.1.post10+localver.1',
                '1.1.post10',
                # '1.1.post10.dev10+local1',
                '1.1.post10.dev10',
                '1.1+local1',
                '1.1',
                # '1.1rc10.post10+local1',
                '1.1rc10.post10',
                # '1.1rc10.post10.dev10+local1',
                '1.1rc10.post10.dev10',
                # '1.1rc9+local1',
                '1.1rc9',
                # '1.1b10.post10+local1',
                '1.1b10.post10',
                # '1.1b10.post10.dev10+local1',
                '1.1b10.post10.dev10',
                # '1.1b10+local1',
                '1.1b10',
                # '1.1a10.post10+local1',
                '1.1a10.post10',
                # '1.1a10.post10.dev10+local1',
                '1.1a10.post10.dev10',
                # '1.1a10+local1',
                '1.1a10',
                # '1.1.dev10+local1',
                '1.1.dev10',
            ],
            '>'
        )
    )
    @unpack
    def test_version_ordering(self, version_chain, op):
        """ version order should be same between pip and zypper"""
        for i, _ in enumerate(version_chain[:-1]):
            self._do_version_compare(version_chain[i], op, version_chain[i+1])
