# TODO
# - lighttpd webapp configuration
Summary:	Integrated scm, wiki, issue tracker and project environment
Summary(pl):	Zintegrowane scm, wiki, system ¶ledzenia problemów i ¶rodowisko projektowe
Name:		trac
Version:	0.9.3
Release:	1
License:	GPL
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/%{name}-%{version}.tar.gz
# Source0-md5:	fce39070081f259020b4d60f044d9082
Source1:	%{name}-apache.conf
Source2:	%{name}.ico
Patch0:		%{name}-util.patch
URL:		http://www.edgewall.com/trac/
BuildRequires:	python >= 1:2.1
BuildRequires:	python-devel >= 1:2.1
BuildRequires:	rpmbuild(macros) >= 1.264
Requires:	group(http)
Requires:	python >= 1:2.1
Requires:	python-clearsilver >= 0.9.3
Requires:	python-sqlite1 >= 0.4.3
Requires:	python-subversion >= 1.2.0
Requires:	subversion >= 1.0.0
Requires:	webapps
# Requires:	apache(mod_env)
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

%description -l pl
Trac to minimalistyczny, oparty na WWW zarz±dca projektów i system
¶ledzenia b³êdów/problemów. Dostarcza interfejs do systemu kontroli
wersji Subversion, zintegrowane wiki, elastyczne ¶ledzenie problemów
i wygodne u³atwienia do raportowania.

%prep
%setup -q
#%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/lib/%{name}}

python ./setup.py install \
	--root=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/htdocs/%{name}.ico
> $RPM_BUILD_ROOT%{_sysconfdir}/htpasswd

# compile the scripts
%{py_ocomp} $RPM_BUILD_ROOT%{py_sitescriptdir}

# remove .py files, leave just compiled ones.
%{py_postclean}

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1
%webapp_register apache %{_webapp}

%triggerun -- apache1
%webapp_unregister apache %{_webapp}

%triggerin -- apache >= 2.0.0
%webapp_register httpd %{_webapp}

%triggerun -- apache >= 2.0.0
%webapp_unregister httpd %{_webapp}

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

%triggerpostun -- %{name} < 0.9.2-0.2
if [ -f /etc/trac/htpasswd.rpmsave ]; then
	mv -f %{_sysconfdir}/htpasswd{,.rpmnew}
	mv -f /etc/trac/htpasswd.rpmsave %{_sysconfdir}/htpasswd
fi

# migrate from apache-config macros
if [ -f /etc/trac/apache.conf.rpmsave ]; then
	if [ -d /etc/apache/webapps.d ]; then
		cp -f %{_sysconfdir}/apache.conf{,.rpmnew}
		cp -f /etc/trac/apache.conf.rpmsave %{_sysconfdir}/apache.conf
	fi

	if [ -d /etc/httpd/webapps.d ]; then
		cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
		cp -f /etc/trac/apache.conf.rpmsave %{_sysconfdir}/httpd.conf
	fi
	rm -f /etc/trac/apache.conf.rpmsave
fi

# register webapp on apaches which were registered earlier
if [ -L /etc/apache/conf.d/99_trac.conf ]; then
	rm -f /etc/apache/conf.d/99_trac.conf
	/usr/sbin/webapp register apache %{_webapp}
	apache_reload=1
fi
if [ -L /etc/httpd/httpd.conf/99_trac.conf ]; then
	rm -f /etc/httpd/httpd.conf/99_trac.conf
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

if [ "$httpd_reload" ]; then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi
if [ "$apache_reload" ]; then
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache reload 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL README THANKS UPGRADE
%doc contrib/
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
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
