# TODO
# - package global files for inheritance, make initial projects use inherit:
#   http://trac.edgewall.org/browser/tags/trac-0.11/RELEASE --
#   [inherit]
#    file = /etc/trac/trac.ini
#    This will load the configuration from the /etc/trac/trac.ini file, while
#    of course allowing to override any global settings in the environment's
#    configuration.
#    In that global configuration, you can specify shared directories for templates and plugins, e.g.:
#    [inherit]
#    plugins_dir = /etc/trac/plugins/
#    templates_dir = /etc/trac/templates/
# - 21:07:41  jtiai> set htdocs_location in trac ini to for example /trac-htdocs/
Summary:	Integrated SCM, Wiki, Issue tracker and project environment
Summary(pl.UTF-8):	Zintegrowane scm, wiki, system śledzenia problemów i środowisko projektowe
Name:		trac
Version:	0.11.7
Release:	3
License:	BSD-like
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/Trac-%{version}.tar.gz
# Source0-md5:	3cd96dad0e4f25d977c422fd6e985e99
Source1:	%{name}-apache.conf
Source2:	%{name}-lighttpd.conf
Source3:	%{name}.ico
Source4:	%{name}.ini
Source5:	%{name}-enableplugin.py
Patch0:		%{name}-root2http.patch
Patch1:		%{name}-defaults.patch
URL:		http://www.edgewall.com/trac/
BuildRequires:	python >= 1:2.1
BuildRequires:	python-devel >= 1:2.1
BuildRequires:	python-setuptools
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
Requires:	group(http)
Requires:	jquery
Requires:	python-clearsilver >= 0.9.3
Requires:	python-trac = %{version}-%{release}
Requires:	webapps
Requires:	webserver(access)
Requires:	webserver(alias)
#Requires:	webserver(rewrite)
#Requires:	webserver(setenv)
#Suggests:	apache(mod_env)
#Suggests:	apache-mod_python >= 3.1.3
#Suggests:	lighttpd-mod_fastcgi
#Suggests:	python-docutils >= 0.6
#Suggests:	python-pygments >= 0.6
#Suggests:	python-silvercity >= 0.9.4
#Suggests:	python-textile >= 2.0
#Suggests:	webserver(auth)
#Suggests:	webserver(cgi)
Obsoletes:	trac-plugin-webadmin
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
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

%package -n python-trac
Summary:	Trac Python modules
Group:		Development/Languages/Python
Requires:	python >= 1:2.1
Requires:	python(sqlite)
Requires:	python-genshi
Requires:	python-setuptools >= 0.6-1.c8.1.1
Requires:	python-subversion >= 1.2.0
Conflicts:	trac < 0.11.4-1.1

%description -n python-trac
Trac Python modules.

%prep
%setup -q -n Trac-%{version}
%patch0 -p1
%patch1 -p1

# using system jquery package
rm trac/htdocs/js/jquery.js

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/lib/%{name}}

%{__python} setup.py install \
	--root=$RPM_BUILD_ROOT

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

# utility script to enable extra plugins
install -p %{SOURCE5} $RPM_BUILD_ROOT%{_bindir}/%{name}-enableplugin

# keep paths from 0.10 install, we want fixed paths so we do not have to update
# webserver config each time with the upgrade.
install -d $RPM_BUILD_ROOT%{_appdir}/cgi-bin
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/trac,%{_appdir}}/htdocs
for a in $RPM_BUILD_ROOT%{py_sitescriptdir}/trac/admin/templates/deploy_trac.*; do
	%{__sed} -i -e 's,${executable},%{__python},g' $a
	mv $a $RPM_BUILD_ROOT%{_appdir}/cgi-bin/${a##*deploy_}
done

cp -a %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/trac.ini
cp -a %{SOURCE3} $RPM_BUILD_ROOT%{_appdir}/htdocs/%{name}.ico
> $RPM_BUILD_ROOT%{_sysconfdir}/htpasswd

# compile the scripts
#%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}

# remove .py files, leave just compiled ones.
%py_postclean

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
%doc contrib
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/htpasswd
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/trac.ini

%attr(755,root,root) %{_bindir}/trac-admin
%attr(755,root,root) %{_bindir}/trac-enableplugin
%attr(755,root,root) %{_bindir}/tracd

#%{_mandir}/man1/trac*.1*

%dir %{_appdir}
%dir %{_appdir}/cgi-bin
%attr(755,root,root) %{_appdir}/cgi-bin/trac.*cgi
%attr(755,root,root) %{_appdir}/cgi-bin/trac.wsgi
%{_appdir}/htdocs
#%{_datadir}/templates
#%{_datadir}/wiki-default
#%{_datadir}/wiki-macros

# project data is stored there
%attr(2770,root,http) %dir /var/lib/trac

%files -n python-trac
%defattr(644,root,root,755)
%{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/Trac-*.egg-info
