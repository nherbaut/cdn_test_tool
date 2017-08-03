import csv
import logging
import subprocess
import urllib
from time import sleep

import dns.resolver
import requests

from dns_handler import update_bind9_dns
from exceptions import MissingDataError


def get_content_ips(dns_server, target=None, klass=dns.resolver.Resolver, timeout=1, lifetime=1, use_bind9=False):
    '''

    :param dns_server:
    :param target:
    :param klass:
    :param timeout:
    :param lifetime:
    :param use_bind9:
    :return:  a tuple containing a list of ip and the hostname of the server from which we are download (can be different from target, as youtube-dl resolves server hostnames for us)
    '''
    from urllib.parse import urlparse

    # check type of target
    if urlparse(target).netloc == '':
        # probaby just a server

        res = klass()
        if use_bind9:
            update_bind9_dns(dns_server)

        res.nameservers = [dns_server]
        res.timeout = timeout
        res.lifetime = lifetime
        try:
            return [ip.address for ip in res.query(target, 'A')], target
        except dns.resolver.NoAnswer:
            raise MissingDataError("No answer from DNS resolver")
    else:
        # probably a content
        # get the cache server hostname, we need to update bind for that
        if use_bind9:
            update_bind9_dns(dns_server)
            # else:
            # print("warning bind configuration not updated")
        content_cache_server_url = get_cache_server_hostname_for_url(target)

        if content_cache_server_url is None:
            # print("failed to get cache server for %s" % target)
            return ([], target)
        else:
            return get_content_ips(dns_server, content_cache_server_url, klass=klass, timeout=timeout,
                                   lifetime=lifetime, use_bind9=use_bind9)


def get_dns_ip_by_country(country, db_path):
    with open(db_path, "r") as f:
        return list(filter(lambda x: x[2] in [country], list(csv.reader(f))))


def get_cache_server_hostname_for_url(content_url):
    '''
    from a content url, check if we can get the url from youtube-dl, if not, return the provided url after all the redirects have been issued
    :param content_url:
    :return: the url of the cache server of None if it cannot be found
    '''
    try:
        proc = subprocess.Popen(["youtube-dl", "-g", content_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while proc.poll() is None:
            sleep(0.1)

        logging.error(proc.stderr.read())
        if proc.poll() == 0:
            server_url = proc.stdout.read().decode("ascii").split("\n")[0]  # bug 2 URL returned?
        else:
            server_url = content_url

        response = None
        while response is None or response.status_code > 299:
            response = requests.head(server_url, allow_redirects=False, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
            if response.status_code > 299 and response.status_code < 399:
                print("nope %s -> %s " % (server_url, response.headers["Location"]))
                server_url = response.headers["Location"]

            elif response.status_code > 399:
                return None

        return urllib.parse.urlparse(server_url).netloc
    except subprocess.CalledProcessError as e:
        logging.error(e)

        return None
