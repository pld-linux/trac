# TODO
# - apache config integration
# - setup and test it :)
# - my first python package, so i have no idea what i'm doing :)
Summary:	Integrated scm, wiki, issue tracker and project environment
Name:		trac
Version:	0.8
Release:	0.1
Epoch:		0
License:	GPL
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/%{name}-%{version}.tar.gz
# Source0-md5:	b21a20affba43cb0cea847f336320257
URL:		http://www.edgewall.com/trac/
BuildRequires:	python >= 2.1
BuildRequires:	sed >= 4.0
Requires:	python >= 2.1
Requires:	python-sqlite >= 0.4.3
Requires:	subversion >= 1.0.0
Requires:	python-clearsilver >= 0.9.3
Requires:	webserver
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define	_sysconfdir	/etc/%{name}

%description
Trac is a minimalistic web-based software project management and
bug/issue tracking system. It provides an interface to the Subversion
revision control systems, an integrated wiki, flexible issue tracking
and convenient report facilities.

%prep
%setup -q

sed -i -e 's|/usr/lib/|%{_libdir}|g' setup.py

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}

python ./setup.py install \
	--root=$RPM_BUILD_ROOT

%{__cat} <<'EOF' > $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
Alias /trac/ "%{_datadir}/trac/htdocs/"

### Trac need to know where the database is located
<Location "/cgi-bin/trac.cgi">
	SetEnv TRAC_DB "%{_datadir}/trac/myproject.db"
</Location>

### You need this to allow users to authenticate
<Location "/cgi-bin/trac.cgi/login">
	AuthType Basic
	AuthName "trac"
	AuthUserFile %{_datadir}/trac/trac.htpasswd
	Require valid-user
</location>
EOF

%{py_comp} $RPM_BUILD_ROOT%{py_sitescriptdir}
%{py_ocomp} $RPM_BUILD_ROOT%{py_sitescriptdir}

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%pre

%post

%preun

%postun

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog COPYING INSTALL README THANKS UPGRADE
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%attr(755,root,root) %{_bindir}/*
%{_datadir}/%{name}
%{_mandir}/man1/trac*.1*

%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}/*.py[co]
%dir %{py_sitescriptdir}/%{name}/mimeviewers
%{py_sitescriptdir}/%{name}/mimeviewers/*.py[co]
%dir %{py_sitescriptdir}/%{name}/upgrades
%{py_sitescriptdir}/%{name}/upgrades/*.py[co]
%dir %{py_sitescriptdir}/%{name}/wikimacros
%{py_sitescriptdir}/%{name}/wikimacros/*.py[co]
