#! /usr/bin/env python3
import argparse
import csv
import json
import logging
import subprocess
import urllib

import dns.resolver
import requests
from geolite2 import geolite2
from haversine import haversine

from dns_handler import update_bind9_dns
from html_output import handle_html

logging.basicConfig(filename='anycastip.log', level=logging.DEBUG)

# limit the number of server we investigate when several server are returned by a DNS query
A_SERVERS_LIMIT = 1


class MissingDataError(Exception):
    pass


def get_distance_in_km(server1, server2):
    if server1.get("location", None) is not None and server2.get("location", None) is not None:
        return haversine(server1["location"], server2["location"])
    else:
        raise MissingDataError()


def get_cache_server_hostname_for_video(video_url):
    '''
    from a video url, use youtube-dl to know which is the hostname of the cache server
    :param video_url:
    :return: the url of the cache server of None if it cannot be found
    '''
    try:
        proc = subprocess.Popen(["youtube-dl", "-g", video_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.error(proc.stderr.read())
        server_url = proc.stdout.read()
        return urllib.parse.urlparse(server_url).netloc
    except subprocess.CalledProcessError as e:
        logging.error(e)

        return None


def get_dns_ip_by_country(country):
    with open("nameservers.csv", "r") as f:
        return [data[0] for data in filter(lambda x: x[2] in [country], list(csv.reader(f)))]


def extract_geoloc_data_ipinfo(ip):
    try:
        response = requests.get("http://ipinfo.io/%s" % (ip))
        if response.ok:

            ipinfo_res = response.json()
            if 'error' in ipinfo_res.keys():
                raise MissingDataError()

            else:
                ip = ipinfo_res.get("ip", "N/A")
                asn = ipinfo_res.get("org", "N/A")
                city = ipinfo_res.get("city", "N/A")
                country = ipinfo_res.get("country", "N/A")
                if ipinfo_res.get("loc", None) is not None:
                    location = list(map(lambda x: float(x), ipinfo_res["loc"].split(",")))
                else:
                    location = None

            return {'ip': ip, 'city': city, 'country': country, 'location': location, 'org': asn}
        else:
            return {'ip': ip, 'city': None, 'country': None, 'location': None, 'org': 'N/A'}
    except requests.exceptions.ConnectionError:
        return {'ip': ip, 'city': None, 'country': None, 'location': None, 'org': 'N/A'}
    except json.decoder.JSONDecodeError:
        return {'ip': ip, 'city': None, 'country': None, 'location': None, 'org': 'N/A'}


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
            raise MissingDataError()
    else:
        # probably a content
        # get the cache server hostname, we need to update bind for that
        if use_bind9:
            update_bind9_dns(dns_server)
            # else:
            # print("warning bind configuration not updated")
        content_cache_server_url = get_cache_server_hostname_for_video(target).decode("ascii")

        if content_cache_server_url is None:
            # print("failed to get cache server for %s" % target)
            return ([], target)
        else:
            return get_content_ips(dns_server, content_cache_server_url, klass=klass, timeout=timeout,
                                   lifetime=lifetime, use_bind9=use_bind9)


def extract_geoloc_data(ip, georeader=geolite2.reader()):
    data = georeader.get(ip)
    if data is not None:
        city = data["city"]["names"]['en'] if data.get('city', None) is not None else None
        country = data['country']["iso_code"] if data.get('country', None) is not None else None
        location = (data['location']["latitude"], data['location']["longitude"]) if data.get('location',
                                                                                             None) is not None else None
        return {'ip': ip, 'city': city, 'country': country, 'location': location}
    else:
        return {'ip': ip, 'city': None, 'country': None, 'location': None}


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='resolve a domain with a list of dns servers, and computer the distance between the DNS server and the resolved server')
    parser.add_argument('-s', '--dns_servers', nargs='+', help='a list of dns servers to compute from', default=None)
    parser.add_argument('--target', '-t', default="md1.libe.com",
                        help='the domain name to resolve or URL of video provider to resolve')
    parser.add_argument('--timeout', default=1, type=float,
                        help='Timeout for the DNS queries')
    parser.add_argument('-c', '--countries', nargs='+', help='a list of countries to select the DNS from', default=None)
    parser.add_argument('--limit', default=10, type=int,
                        help='Maximum number of dns servers to query')
    parser.add_argument('--use_bind9', action='store_true',
                        help='use bind9 to change DNS resolver')
    parser.add_argument('--list-countries', action='store_true',
                        help='use bind9 to change DNS resolver')
    parser.add_argument('--output-format', default="plain",
                        help='format of the output, one of "plain, simple, grid, fancy_grid, pipe, orgtbl, jira, psql, rst, mediawiki, moinmoin, html, latex, latex_booktabs, textile"')
    parser.add_argument('-dns-db', help="name of the dns database file",
                        default="nameservers.csv")

    args = parser.parse_args()

    client_infos = extract_geoloc_data_ipinfo("")

    if args.list_countries is True:
        with open(args.dns_db, "r") as f:
            # print(" ".join(["%s(%3d)" % (k, v) for k, v insorted(Counter(line[2] for line in list(csv.reader(f))).items(), key=lambda x: -x[1])]))
            print(" ".join(sorted({line[2] for line in list(csv.reader(f))})))
            exit(0)

    target = args.target

    # if we require a specific list of countries
    if args.countries is not None:
        dnsips = set().union(*[get_dns_ip_by_country(country)[:args.limit] for country in args.countries])
    else:
        # if we didn't specifies a target dns_server to test
        if args.dns_servers is None:
            with open(args.dns_db) as f:
                reader = csv.reader(f)
                dnsips = [line[0] for line in list(reader)[:args.limit]]

        else:
            # take all the dns server we have
            dnsips = args.dns_servers[:args.limit]

    reader = geolite2.reader()

    if args.use_bind9:
        update_bind9_dns("8.8.8.8")

    # get the informations from the dns servers from the csv file
    dns_servers_infoss = [extract_geoloc_data_ipinfo(dnsip) for dnsip in sorted(dnsips)]

    distance_content_dnss = []
    distance_content_mes = []
    data = []
    # do this for every dns server we have
    for dns_server_index, dns_server_infos in enumerate(dns_servers_infoss, 1):
        dns_server_ip, dns_server_country = dns_server_infos["ip"], dns_server_infos["country"]

        try:
            resolved_ips, resolved_target = get_content_ips(dns_server_ip, target=target, timeout=args.timeout,
                                                            lifetime=args.timeout,
                                                            use_bind9=args.use_bind9)

            # resolved_infos = extract_geoloc_data(resolved_ips[0])
            # resolved_infos = min([candiate_info for candiate_info in[extract_geoloc_data_ipinfo(resolved_ip) for resolved_ip in resolved_ips]],key=lambda x: get_distance_in_km(my_data, x))
            for resolved_info_index, resolved_infos in enumerate([candiate_info for candiate_info in
                                                                  [extract_geoloc_data_ipinfo(resolved_ip) for
                                                                   resolved_ip in resolved_ips]][:A_SERVERS_LIMIT], 1):
                asn = resolved_infos.get("org", "N/A")
                distance_content_dns = get_distance_in_km(dns_server_infos, resolved_infos)
                distance_content_me = get_distance_in_km(client_infos, resolved_infos)
                distance_content_dnss.append(distance_content_dns)
                distance_content_mes.append(distance_content_me)

                # replace none distance by N/A
                distance_content_dns = str(int(distance_content_dns)) if distance_content_dns is not None else "N/A"
                distance_content_me = str(int(distance_content_me)) if distance_content_me is not None else "N/A"

                data.append({
                    "Index": "%02d.%02d" % (dns_server_index, resolved_info_index),
                    "dns_ip": dns_server_ip,
                    "cont_ip": resolved_infos["ip"],
                    "my_ip": client_infos["ip"],
                    "dns_iso": dns_server_country,
                    "content_iso": resolved_infos["country"],
                    "me_iso": client_infos["country"],
                    "cnd_count_km": distance_content_dns,
                    "me_count_km": distance_content_me,
                    "dns_as": dns_server_infos.get("org", "N/A"),
                    "cont_as": asn,
                    "cont_hst": resolved_target,
                    "dns_loc": dns_server_infos["location"],
                    "content_loc": resolved_infos["location"],
                    "me_loc": client_infos["location"],
                })

        except (dns.exception.Timeout, MissingDataError)  as e:
            logging.error(e)
            continue

    avg_distance_dns = sum(distance_content_dnss) / len(distance_content_dnss)
    avg_distance_me = sum(distance_content_mes) / len(distance_content_mes)

    avg_distance_dns = str(int(avg_distance_dns)) if avg_distance_dns is not None else "N/A"
    avg_distance_me = str(int(avg_distance_me)) if avg_distance_me is not None else "N/A"

    data.append({
        "Index": "avg",
        "dns_ip": "",
        "cont_ip": "",
        "my_ip": "",
        "dns_iso": "",
        "content_iso": "",
        "me_iso": "",
        "cnd_count_km": avg_distance_dns,
        "me_count_km": avg_distance_me,
        "dns_as": "",
        "cont_as": "",
        "cont_hst": ""

    })

    from tabulate import tabulate

    if args.output_format == "html":
        print(handle_html(data))
    else:
        print(tabulate(data, tablefmt=args.output_format, headers="keys"))

    with open("output.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:-1])
