Summary:	Integrated scm, wiki, issue tracker and project environment
Summary(pl.UTF-8):	Zintegrowane scm, wiki, system śledzenia problemów i środowisko projektowe
Name:		trac
Version:	0.10.4
Release:	4
License:	BSD-like
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/%{name}-%{version}.tar.gz
# Source0-md5:	52a3a21ad9faafc3b59cbeb87d5a69d2
Source1:	%{name}-apache.conf
Source2:	%{name}-lighttpd.conf
Source3:	%{name}.ico
Patch0:		%{name}-util.patch
Patch1:		%{name}-root2http.patch
URL:		http://www.edgewall.com/trac/
BuildRequires:	python >= 1:2.1
BuildRequires:	python-devel >= 1:2.1
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	group(http)
Requires:	python >= 1:2.1
Requires:	python-clearsilver >= 0.9.3
Requires:	python-sqlite1 >= 0.4.3
Requires:	python-subversion >= 1.2.0
Requires:	subversion >= 1.0.0
Requires:	webapps
Requires:	webserver(access)
Requires:	webserver(alias)
#Requires:	webserver(auth)
#Requires:	webserver(env)
#Requires:	webserver(rewrite)
#Suggests:	apache(mod_env)
#Suggests:	apache-mod_python >= 3.1.3
#Suggests:	lighttpd-mod_fastcgi
#Suggests:	webserver(cgi)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_datadir	%{_prefix}/share/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
Trac is a minimalistic web-based software project management and
bug/issue tracking system. It provides an interface to the Subversion
revision control systems, an integrated wiki, flexible issue tracking
and convenient report facilities.

%description -l pl.UTF-8
Trac to minimalistyczny, oparty na WWW zarządca projektów i system
śledzenia błędów/problemów. Dostarcza interfejs do systemu kontroli
wersji Subversion, zintegrowane wiki, elastyczne śledzenie problemów i
wygodne ułatwienia do raportowania.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/lib/%{name}}

python ./setup.py install \
	--root=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/htdocs/%{name}.ico
> $RPM_BUILD_ROOT%{_sysconfdir}/htpasswd

# compile the scripts
%{py_ocomp} $RPM_BUILD_ROOT%{py_sitescriptdir}

# remove .py files, leave just compiled ones.
%{py_postclean}

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%post
if [ "$1" = 1 ]; then
%banner %{name} -e <<EOF

To create new trac environment run as root:
# trac-admin /var/lib/trac/project initenv
and chown -R it to webserver user (http).

EOF
#'

# NOTE(s)
#- we made the parent directory (/var/lib/trac) g+s, but db/* files
#  needed to be really writable for web user, so better suggest
#  chown -R than chmod single file(s)?

fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL README THANKS UPGRADE
%doc contrib/
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/htpasswd

%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/trac*.1*

# project data is stored there
%attr(2770,root,http) %dir /var/lib/trac

%dir %{_datadir}
%dir %{_datadir}/cgi-bin
%attr(755,root,root) %{_datadir}/cgi-bin/trac.*cgi
%{_datadir}/htdocs
%{_datadir}/templates
%{_datadir}/wiki-default
%{_datadir}/wiki-macros

%{py_sitescriptdir}/%{name}
