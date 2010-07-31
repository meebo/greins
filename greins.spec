#!/bin/sh
python setup.py install --single-version-externally-managed --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

ls
pwd
install -D -m 755 greins.init $RPM_BUILD_ROOT%{_initrddir}/greins
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/greins/conf.d
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/greins
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/greins
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -D -m 644 greins.conf $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/greins

EXTRA_FILES="\
%{_initrddir}/greins
%dir %{_sysconfdir}/greins/conf.d
%dir %attr(0755, root, root) %{_localstatedir}/log/greins
%dir %attr(0755, root, root) %{_localstatedir}/run/greins
%config(noreplace) %{_sysconfdir}/sysconfig/greins
"
echo "$EXTRA_FILES" | cat INSTALLED_FILES - > INSTALLED_FILES.new
mv INSTALLED_FILES.new INSTALLED_FILES
