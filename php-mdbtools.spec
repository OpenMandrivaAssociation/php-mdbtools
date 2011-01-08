%define modname mdbtools
%define soname %{modname}.so
%define inifile A69_%{modname}.ini

Summary:	MDB data file access library
Name:		php-%{modname}
Version:	1.0.0
Release:	%mkrel 18
Group:		Development/PHP
License:	LGPL
URL:		http://pecl.php.net/package/mdbtools
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-mod_php
BuildRequires:	php-devel >= 3:5.2.0
BuildRequires:	libmdbtools-devel
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mdbtools provides read access to MDB data files as used by Microsoft Access and
its underlying JetEngine.

It is based on libmdb from the mdbtools package available at
http://mdbtools.sourceforge.net/

%prep

%setup -q -n %{modname}-%{version}
[ "../package*.xml" != "/" ] && mv ../package*.xml .

# fix permissions
find . -type f | xargs chmod 644

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" config.m4

%build
%serverbuild

phpize
%configure2_5x --with-libdir=%{_lib} \
    --with-%{modname}=shared,%{_prefix}

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}/var/log/httpd

install -m0755 modules/%{soname} %{buildroot}%{_libdir}/php/extensions/

cat > %{buildroot}%{_sysconfdir}/php.d/%{inifile} << EOF
extension = %{soname}
EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%doc package*.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}
