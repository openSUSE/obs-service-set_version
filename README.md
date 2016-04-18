# set_version (OBS source service) [![Build Status](https://travis-ci.org/openSUSE/obs-service-set_version.svg?branch=master)](https://travis-ci.org/openSUSE/obs-service-set_version)

This service updates a RPM spec or Debian changelog according to the existing files.
The service can be used in combination with other services like [download_files](https://github.com/openSUSE/obs-service-download_files)
or [tar_scm](https://github.com/openSUSE/obs-service-tar_scm).
This is the git repository for [openSUSE:Tools/obs-service-set_version](https://build.opensuse.org/package/show/openSUSE:Tools/obs-service-set_version).
The authoritative source is https://github.com/openSUSE/obs-service-set_version

## Dependencies
Install the following deps:

    zypper in python-packaging


## Test suite
To run the full testsuite, some dependencies are needed:

    zypper in devscripts dpkg python-tox

If the dependencies are not installed, some tests are skipped. `zypper` itself
is also needed for the tests with python packages and PEP440 compatible versions.

To run the testsuite, execute:

    tox -epy27

The testrun may take some time.
