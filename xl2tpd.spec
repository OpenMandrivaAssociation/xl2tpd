Summary:	Layer 2 Tunnelling Protocol Daemon (RFC 2661)
Name:		xl2tpd
Version:	1.3.6
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://www.xelerance.com/software/xl2tpd/
Source0:	http://www.xelerance.com/software/xl2tpd/%{name}-%{version}.tar.gz
BuildRequires:	pcap-devel
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

%prep
%setup -q

%build
export CC=gcc
%make DFLAGS="%{optflags} -g -DDEBUG_PPPD -DDEBUG_CONTROL -DDEBUG_ENTROPY"
sed -i -e 's|chkconfig:[ \t][ \t]*|chkconfig: |' packaging/fedora/xl2tpd.init

%install
%makeinstall_std PREFIX="%{_prefix}"
install -p -D -m644 examples/xl2tpd.conf %{buildroot}%{_sysconfdir}/xl2tpd/xl2tpd.conf
install -p -D -m644 examples/ppp-options.xl2tpd %{buildroot}%{_sysconfdir}/ppp/options.xl2tpd
install -p -D -m600 doc/l2tp-secrets.sample %{buildroot}%{_sysconfdir}/xl2tpd/l2tp-secrets
install -p -D -m600 examples/chapsecrets.sample %{buildroot}%{_sysconfdir}/ppp/chap-secrets.sample
install -p -D -m755 packaging/fedora/xl2tpd.init %{buildroot}%{_initrddir}/xl2tpd
install -p -D -m755 -d %{buildroot}%{_localstatedir}/run/xl2tpd

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

%files
%doc BUGS CHANGES CREDITS LICENSE README.* TODO doc/rfc2661.txt 
%doc doc/README.patents examples/chapsecrets.sample
%{_sbindir}/xl2tpd
%{_sbindir}/xl2tpd-control
%{_bindir}/pfc
%{_mandir}/*/*
%dir %{_sysconfdir}/xl2tpd
%config(noreplace) %{_sysconfdir}/xl2tpd/*
%config(noreplace) %{_sysconfdir}/ppp/*
%attr(0755,root,root)  %{_initrddir}/xl2tpd
%dir %{_localstatedir}/run/xl2tpd

