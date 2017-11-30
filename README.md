# set_version (OBS source service) [![Build Status](https://travis-ci.org/openSUSE/obs-service-set_version.svg?branch=master)](https://travis-ci.org/openSUSE/obs-service-set_version)

This is an [Open Build Service](http://openbuildservice.org/) source service. It updates an RPM spec or Debian changelog according to the existing files.

This is the git repository for [openSUSE:Tools/obs-service-set_version](https://build.opensuse.org/package/show/openSUSE:Tools/obs-service-set_version). The authoritative source is https://github.com/openSUSE/obs-service-set_version
 
The service can be used in combination with other services like [download_files](https://github.com/openSUSE/obs-service-download_files), [tar_scm](https://github.com/openSUSE/obs-service-tar_scm), [recompress](https://github.com/openSUSE/obs-service-recompress) or [extract_file](https://github.com/openSUSE/obs-service-extract_file) e.g. within the [GIT integration](https://en.opensuse.org/openSUSE:Build_Service_Concept_SourceService#Example_2:_GIT_integration) workflow.

## Dependencies
Install the following deps:

    zypper in python-packaging


## Test suite
To run the full testsuite, some dependencies are needed:

    zypper in devscripts dpkg

If the dependencies are not installed, some tests are skipped. `zypper` itself
is also needed for the tests with python packages and PEP440 compatible versions.

To run the testsuite, execute:

    python -m unittest discover tests/

The testrun may take some time. Don't forget to run also

    flake8 set_version tests/



