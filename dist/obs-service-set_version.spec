#
# spec file for package obs-service-set_version
#
# Copyright (c) 2024 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%if 0%{?suse_version} >= 1500 || 0%{?fedora_version} >= 29 || 0%{?centos_version} >= 800
%bcond_without python3
%else
%bcond_with    python3
%endif
%if %{with python3}
%define use_python python3
%else
%define use_python python
%endif

%define service set_version

Name:           obs-service-%{service}
Version:        0.5.12
Release:        0
Summary:        An OBS source service: Update spec file version
License:        GPL-2.0-or-later
Group:          Development/Tools/Building
URL:            https://github.com/openSUSE/obs-service-%{service}
Source:         %{name}-%{version}.tar.gz
BuildRequires:  python3-ddt
BuildRequires:  python3-flake8
BuildRequires:  python3-packaging
%if 0%{?suse_version}
%if 0%{?suse_version} > 1315
Recommends:     python3-packaging
Requires:       python3-base
%else
Recommends:     python-packaging
%endif
%endif
Requires:       sed
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
This is a source service for openSUSE Build Service.

Very simply script to update the version in .spec or .dsc files according to
a given version or to the existing files.

%prep
%setup -q

%build
%if 0%{?suse_version} > 1315
sed -i -e "1 s,#!/usr/bin/python$,#!/usr/bin/python3," set_version
%endif

%check
make test PYTHON=python3

%install
mkdir -p %{buildroot}%{_prefix}/lib/obs/service
install -m 0755 set_version %{buildroot}%{_prefix}/lib/obs/service
install -m 0644 set_version.service %{buildroot}%{_prefix}/lib/obs/service
perl -p -i -e 's{#!.*python.*}{#!%{_bindir}/%{use_python}}' %{buildroot}%{_prefix}/lib/obs/service/set_version

%files
%defattr(-,root,root)
%dir %{_prefix}/lib/obs
%{_prefix}/lib/obs/service

%changelog
