# TODO
# - localization fix in files
# - 21:07:41  jtiai> set htdocs_location in trac ini to for example /trac-htdocs/
Summary:	Integrated SCM, Wiki, Issue tracker and project environment
Summary(pl.UTF-8):	Zintegrowane scm, wiki, system śledzenia problemów i środowisko projektowe
Name:		trac
# NOTE 1.0 is on DEVEL branch, finish it there and then merge
Version:	0.12.5
Release:	1
License:	BSD-like
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/Trac-%{version}.tar.gz
# Source0-md5:	9ff5adef035fc8f88cc54a714288ee9b
Source1:	%{name}-apache.conf
Source2:	%{name}-lighttpd.conf
Source3:	%{name}.ico
Source4:	%{name}.ini
Source5:	%{name}-enableplugin.py
Source6:	%{name}-upgrade.py
Patch0:		%{name}-root2http.patch
Patch1:		%{name}-defaults.patch
Patch2:		inherit-global-%{name}.ini.patch
Patch3:		silvercity-javascript-mimetypes.patch
URL:		http://trac.edgewall.org/
BuildRequires:	python >= 1:2.1
BuildRequires:	python-babel >= 0.9.5
BuildRequires:	python-devel >= 1:2.1
BuildRequires:	python-distribute
BuildRequires:	python-genshi
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
#Requires:	apache(mod_env) || lighttpd-mod_fastcgi
Requires:	group(http)
Requires:	jquery
Requires:	python-clearsilver >= 0.9.3
Requires:	python-trac = %{version}-%{release}
Requires:	webapps
Requires:	webserver(access)
Requires:	webserver(alias)
Requires:	webserver(auth)
Requires:	webserver(cgi)
Requires:	webserver(mime)
Requires:	webserver(rewrite)
# TODO
# If apache is the webserver, apache-mod_python is required! What can do?
#Suggests:	apache-mod_python >= 3.1.3
#Suggests:	lighttpd-mod_fastcgi
#Suggests:	python-textile >= 2.0
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
Requires:	python >= 1:2.4
# python-distribute for pkg_resources module
Requires:	python-distribute
Requires:	python-genshi >= 0.6
Requires:	python-sqlite >= 2.5.5
Requires:	python-subversion >= 1.2.0
Suggests:	python-babel >= 0.9.5
Suggests:	python-docutils >= 0.6
Suggests:	python-pygments >= 0.6
Suggests:	python-pytz
Conflicts:	trac < 0.11.7-3

%description -n python-trac
Trac Python modules.

%prep
%setup -q -n Trac-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

# using system jquery package
rm trac/htdocs/js/jquery.js

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sbindir},/var/lib/%{name},%{_datadir}/%{name}/{plugins,templates}}

%{__python} setup.py install \
	--skip-build \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

# utility script to enable extra plugins
install -p %{SOURCE5} $RPM_BUILD_ROOT%{_sbindir}/%{name}-enableplugin
# handle upgrades
install -p %{SOURCE6} $RPM_BUILD_ROOT%{_sbindir}/%{name}-upgrade

# keep paths from 0.10 install, we want fixed paths so we do not have to update
# webserver config each time with the upgrade.
install -d $RPM_BUILD_ROOT%{_appdir}/cgi-bin
mv $RPM_BUILD_ROOT{%{py_sitescriptdir}/trac,%{_appdir}}/htdocs

rm $RPM_BUILD_ROOT%{_appdir}/htdocs/README

install -p cgi-bin/trac.*  $RPM_BUILD_ROOT%{_appdir}/cgi-bin

cp -a %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/trac.ini
cp -a %{SOURCE3} $RPM_BUILD_ROOT%{_appdir}/htdocs/%{name}.ico
> $RPM_BUILD_ROOT%{_sysconfdir}/htpasswd

# remove .py files, leave just compiled ones.
%py_postclean

# we don't need these runtime
rm -rf $RPM_BUILD_ROOT%{py_sitescriptdir}/trac/tests

# collect lang files
echo "%dir %{_appdir}/htdocs/js/messages" > %{name}.lang
for a in $RPM_BUILD_ROOT%{_appdir}/htdocs/js/messages/*.js; do
	f=${a##*/}
	l=${f%.js}
	echo "%lang($l) ${a#$RPM_BUILD_ROOT}"
done >> %{name}.lang

# TODO: move to /usr/share/locale as trac.mo catalog
echo "%dir %{py_sitescriptdir}/trac/locale" >> %{name}.lang
for a in $RPM_BUILD_ROOT%{py_sitescriptdir}/trac/locale/*/LC_MESSAGES/*.mo; do
	d=${a%%/LC_MESSAGES*}
	l=${d##*/}
	echo "%lang($l) ${d#$RPM_BUILD_ROOT}"
done >> %{name}.lang

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

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL README THANKS UPGRADE
%doc contrib
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/htpasswd
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/trac.ini

%attr(755,root,root) %{_sbindir}/trac-enableplugin
%attr(755,root,root) %{_sbindir}/trac-upgrade
%attr(755,root,root) %{_bindir}/tracd

#%{_mandir}/man1/trac*.1*

%dir %{_appdir}
%dir %{_appdir}/cgi-bin
%attr(755,root,root) %{_appdir}/cgi-bin/trac.cgi
%attr(755,root,root) %{_appdir}/cgi-bin/trac.fcgi
%dir %{_appdir}/htdocs
%dir %{_appdir}/plugins
%dir %{_appdir}/templates
%{_appdir}/htdocs/*.gif
%{_appdir}/htdocs/*.ico
%{_appdir}/htdocs/*.png
%{_appdir}/htdocs/css
%{_appdir}/htdocs/guide

%dir %{_appdir}/htdocs/js
%{_appdir}/htdocs/js/*.js

# keep upgrade data in main pkg only
%{py_sitescriptdir}/trac/upgrades

# project data is stored there
%attr(2770,root,http) %dir /var/lib/trac

%files -n python-trac
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/trac-admin

%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/trac/*.py[co]
%dir %{py_sitescriptdir}/trac/locale
%{py_sitescriptdir}/trac/admin
%{py_sitescriptdir}/trac/db
%{py_sitescriptdir}/trac/mimeview
%{py_sitescriptdir}/trac/prefs
%{py_sitescriptdir}/trac/search
%{py_sitescriptdir}/trac/templates
%{py_sitescriptdir}/trac/ticket
%{py_sitescriptdir}/trac/timeline
%{py_sitescriptdir}/trac/util
%{py_sitescriptdir}/trac/versioncontrol
%{py_sitescriptdir}/trac/web
%{py_sitescriptdir}/trac/wiki

%{py_sitescriptdir}/%{name}opt
%{py_sitescriptdir}/Trac-*.egg-info
