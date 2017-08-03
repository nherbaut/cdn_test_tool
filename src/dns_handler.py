#! /usr/bin/env python3

import subprocess
from jinja2 import Template
import logging




def update_bind9_dns(dns_server):
    import os
    with open("templates/named.conf.options.tpl", "r") as f:
        t = Template(f.read())
        with open("/etc/bind/named.conf.options", "w") as bind_conf_file:
            bind_conf_file.write(t.render(dns_server=dns_server))
        proc = subprocess.Popen(["service", "bind9", "restart"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        logging.info(proc.stdout.read())
        logging.info(proc.stderr.read())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='updated forwarders of a local bind9 install')
    parser.add_argument('-s', '--dns_server', help='a list of dns servers to compute from', default="8.8.8.8")
    args = parser.parse_args()
    update_bind9_dns(args.dns_server)
