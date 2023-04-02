Summary:	Layer 2 Tunnelling Protocol Daemon (RFC 2661)
Name:		xl2tpd
Version:	1.3.18
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		https://github.com/xelerance/xl2tpd/
Source0:	https://github.com/xelerance/xl2tpd/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:	%{name}.service
Source2:	%{name}.tmpfiles
BuildRequires:	pkgconfig(libpcap)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	systemd-units

Requires:	ppp

Requires(post,preun):	rpm-helper
Requires(preun):	rpm-helper

%description
xl2tpd is an implementation of the Layer 2 Tunnelling Protocol (RFC 2661).
L2TP allows you to tunnel PPP over UDP. Some ISPs use L2TP to tunnel user
sessions from dial-in servers (modem banks, ADSL DSLAMs) to back-end PPP
servers. Another important application is Virtual Private Networks where
the IPsec protocol is used to secure the L2TP connection (L2TP/IPsec,
RFC 3193). The L2TP/IPsec protocol is mainly used by Windows and 
Mac OS X clients. On Linux, xl2tpd can be used in combination with IPsec
implementations such as Openswan.
Example configuration files for such a setup are included in this RPM.

xl2tpd works by opening a pseudo-tty for communicating with pppd.
It runs completely in userspace.

%files
%license LICENSE
%doc BUGS CHANGES CREDITS README.* TODO
%doc doc/README.patents examples/chapsecrets.sample
%{_sbindir}/xl2tpd
%{_sbindir}/xl2tpd-control
%{_bindir}/pfc
%{_mandir}/*/*
%dir %{_sysconfdir}/xl2tpd
%config(noreplace) %{_sysconfdir}/xl2tpd/*
%config(noreplace) %{_sysconfdir}/ppp/*
#attr(0755,root,root)  %{_initrddir}/xl2tpd
#dir %{_localstatedir}/run/xl2tpd
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf
%dir %{_rundir}/xl2tpd
%ghost %attr(0600,root,root) %{_rundir}/xl2tpd/l2tp-control

#---------------------------------------------------------------------------

%prep
%autosetup -p1

%build
export CFLAGS="$CFLAGS -fPIC -Wall -DTRUST_PPPD_TO_DIE"
export DFLAGS="%{optflags} -g"
#export DFLAGS="%{optflags} -g -DDEBUG_HELLO -DDEBUG_CLOSE -DDEBUG_FLOW -DDEBUG_PAYLOAD -DDEBUG_CONTROL -DDEBUG_CONTROL_XMIT -DDEBUG_FLOW_MORE -DDEBUG_MAGIC -DDEBUG_ENTROPY -DDEBUG_HIDDEN -DDEBUG_PPPD -DDEBUG_AAA -DDEBUG_FILE -DDEBUG_FLOW -DDEBUG_HELLO -DDEBUG_CLOSE -DDEBUG_ZLB -DDEBUG_AUTH"
export LDFLAGS="$LDFLAGS -pie -Wl,-z,relro -Wl,-z,now"

# fixup for obsoleted pppd options
sed -i -e "s/crtscts/#obsolete: crtscts/" examples/ppp-options.xl2tpd
sed -i -e "s/lock/#obsolete: lock/" examples/ppp-options.xl2tpd
%before_configure
%make_build

%install
%make_install PREFIX="%{_prefix}" SBINDIR="%{buildroot}%{_bindir}"

#install -dm 0755 %{buildroot}%{_unitdir}
install -D -pm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/xl2tpd.service

#install -dm 0755 %{buildroot}/%{_tmpfilesdir}
install -D -pm 0644 %{SOURCE2} %{buildroot}/%{_tmpfilesdir}/%{name}.conf

install -D -pm 0644 examples/xl2tpd.conf %{buildroot}%{_sysconfdir}/xl2tpd/xl2tpd.conf
install -D -pm 0644 examples/ppp-options.xl2tpd %{buildroot}%{_sysconfdir}/ppp/options.xl2tpd
install -D -pm 0600 examples/chapsecrets.sample %{buildroot}%{_sysconfdir}/ppp/chap-secrets.sample
install -D -pm 0600 doc/l2tp-secrets.sample %{buildroot}%{_sysconfdir}/xl2tpd/l2tp-secrets

install -D -dm 0755 %{buildroot}%{_rundir}/xl2tpd

#install -D -pm 0755 packaging/fedora/xl2tpd.init %{buildroot}%{_initrddir}/xl2tpd

%post
/sbin/chkconfig --add xl2tpd
# if we migrate from l2tpd to xl2tpd, copy the configs
if [ -f /etc/l2tpd/l2tpd.conf ]
then
	echo "Old /etc/l2tpd configuration found, migrating to /etc/xl2tpd"
	mv /etc/xl2tpd/xl2tpd.conf /etc/xl2tpd/xl2tpd.conf.rpmsave
	cat /etc/l2tpd/l2tpd.conf | sed "s/options.l2tpd/options.xl2tpd/" > /etc/xl2tpd/xl2tpd.conf
	mv /etc/ppp/options.xl2tpd /etc/ppp/options.xl2tpd.rpmsave
	mv /etc/ppp/options.l2tpd /etc/ppp/options.xl2tpd
	mv /etc/xl2tpd/l2tp-secrets /etc/xl2tpd/l2tpd-secrets.rpmsave
	cp -pa /etc/l2tpd/l2tp-secrets /etc/xl2tpd/l2tp-secrets
	
fi

%preun
if [ $1 -eq 0 ]; then
	/sbin/service xl2tpd stop > /dev/null 2>&1
	/sbin/chkconfig --del xl2tpd
fi

%postun
if [ $1 -ge 1 ]; then
  /sbin/service xl2tpd condrestart 2>&1 >/dev/null
fi

