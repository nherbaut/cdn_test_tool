options {
        directory "/var/cache/bind";
        forwarders {
		{{ dns_server }};
        };
        dnssec-validation auto;
        auth-nxdomain no;    # conform to RFC1035
        listen-on-v6 { any; };
};
