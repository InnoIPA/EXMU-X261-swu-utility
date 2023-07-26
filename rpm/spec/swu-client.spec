Name: swu-client
Summary: OTA for EXMU-X261
# Version: %(git symbolic-ref HEAD | sed -e "s/^refs\/heads\///")
Version: 0.0.1
Release: 1
License: MIT

# https://superuser.com/a/557112
AutoReqProv: no

%description
swu-client service

%define _pwd %(echo $PWD)
%define _rpmdir %(echo $PWD)/rpm

%define systemd_service /lib/systemd/system
%define systemd_preset /lib/systemd/system-preset

%build
cd %{_pwd}
python3 setup.py build

%install
cd %{_pwd}
%define prefix /usr

# python package
python3 setup.py install --root=%{buildroot} --record=INSTALLED_FILES  --prefix=%{prefix} --optimize=1

# FIXME
# hack executable shebang line
# https://git.openembedded.org/openembedded-core/tree/meta/classes/distutils3.bbclass?h=honister#n46
sed -i  's:^#!/.*/python3$:#!/usr/bin/env python3:' %{buildroot}%{prefix}/bin/*

# systemd stuff
install -m 644 -D systemd/swu-client.service %{buildroot}/%{systemd_service}/swu-client.service

mkdir -p %{buildroot}/%{systemd_preset}
echo "enable swu-client.service" > %{buildroot}/%{systemd_preset}/98-swu-client.preset

# configuration file
install -m 644 -D src/swu_utility/config/ipat4.ini %{buildroot}/opt/innodisk/swu-client/config.ini

# swupdate handler
install -m 644 -D swupdate_handlers/swupdate_handlers.lua %{buildroot}/opt/innodisk/swu-client/swupdate_handlers.lua

%clean
rm -rf %{_pwd}/build
rm -rf %{buildroot}
rm -rf %{_pwd}/INSTALLED_FILES

%post
systemctl daemon-reload
systemctl enable --now swu-client.service

%files -f %{_pwd}/INSTALLED_FILES
%{systemd_service}/swu-client.service
%{systemd_preset}/98-swu-client.preset
/opt/innodisk/swu-client/*
