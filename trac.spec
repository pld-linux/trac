Summary:	Integrated scm, wiki, issue tracker and project environment
Summary(pl):	Zintegrowane scm, wiki, system ¶ledzenia problemów i ¶rodowisko projektowe
Name:		trac
Version:	0.8.4
Release:	2
Epoch:		0
License:	GPL
Group:		Applications/WWW
Source0:	http://ftp.edgewall.com/pub/trac/%{name}-%{version}.tar.gz
# Source0-md5:	e2b1d0e49deea72928d59ed406a8fc87
Source1:	%{name}-apache.conf
Source2:	%{name}.ico
Patch0:	%{name}-util.patch
URL:		http://www.edgewall.com/trac/
BuildRequires:	python >= 2.1
BuildRequires:	rpmbuild(macros) >= 1.177
Requires:	group(http)
Requires:	python >= 2.1
Requires:	python-clearsilver >= 0.9.3
Requires:	python-sqlite1 >= 0.4.3
Requires:	python-subversion >= 1.2.0
Requires:	subversion >= 1.0.0
Requires:	webserver
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/%{name}
%define		_datadir	%{_prefix}/share/%{name}
%define		_apache1dir	/etc/apache
%define		_apache2dir	/etc/httpd

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
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/lib/%{name}}

python ./setup.py install \
	--root=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/htdocs/%{name}.ico
> $RPM_BUILD_ROOT%{_sysconfdir}/htpasswd

# compile the scripts
%{py_ocomp} $RPM_BUILD_ROOT%{py_sitescriptdir}

# remove .py files, leave just compiled ones.
#%%{py_postclean}

%clean
rm -rf $RPM_BUILD_ROOT

%post
# apache1
if [ -d %{_apache1dir}/conf.d ]; then
	ln -sf %{_sysconfdir}/apache.conf %{_apache1dir}/conf.d/99_%{name}.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi
# apache2
if [ -d %{_apache2dir}/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache.conf %{_apache2dir}/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

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

%preun
if [ "$1" = "0" ]; then
	# apache1
	if [ -d %{_apache1dir}/conf.d ]; then
		rm -f %{_apache1dir}/conf.d/99_%{name}.conf
		if [ -f /var/lock/subsys/apache ]; then
			/etc/rc.d/init.d/apache restart 1>&2
		fi
	fi
	# apache2
	if [ -d %{_apache2dir}/httpd.conf ]; then
		rm -f %{_apache2dir}/httpd.conf/99_%{name}.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/etc/rc.d/init.d/httpd restart 1>&2
		fi
	fi
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL README THANKS UPGRADE
%dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
# this group makes it apache specific?
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/htpasswd
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/trac*.1*

# project data is stored there
%attr(2770,root,http) %dir /var/lib/trac

%dir %{_datadir}
%dir %{_datadir}/cgi-bin
%attr(755,root,root) %{_datadir}/cgi-bin/trac.cgi
%{_datadir}/htdocs
%{_datadir}/templates
%{_datadir}/wiki-default

%dir %{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}/*.py[co]
%dir %{py_sitescriptdir}/%{name}/mimeviewers
%{py_sitescriptdir}/%{name}/mimeviewers/*.py[co]
%dir %{py_sitescriptdir}/%{name}/upgrades
%{py_sitescriptdir}/%{name}/upgrades/*.py[co]
%dir %{py_sitescriptdir}/%{name}/wikimacros
%{py_sitescriptdir}/%{name}/wikimacros/*.py[co]
