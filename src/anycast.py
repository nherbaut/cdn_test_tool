#! /usr/bin/env python3
import argparse
import csv
import logging
import urllib.request

import dns.resolver
from geolite2 import geolite2
from haversine import haversine

from content_extraction import get_content_ips, get_dns_ip_by_country
from dns_handler import update_bind9_dns
from exceptions import MissingDataError
from geoloc import extract_geoloc_data, extract_geoloc_data_from_csv_line
from pretty_printer import write_output

logging.basicConfig(filename='anycastip.log', level=logging.DEBUG)

# limit the number of server we investigate when several server are returned by a DNS query
A_SERVERS_LIMIT = 1

from scapy.all import *
from collections import OrderedDict


def get_route_to(ip):
    return get_route_to_ip_scapy(ip)


def get_route_to_ip_scapy(ip):
    try:
        # result, _ = traceroute(ip, l4=UDP(sport=RandShort()))
        result, _ = traceroute(ip)
        ips = [v[0] for k, v in
               sorted(result.get_trace()[ip].items(), key=lambda x: x[0])]

        ips = list(OrderedDict.fromkeys(ips))
        return list(filter(lambda x: x[1] is not None, [(ip, extract_geoloc_data(ip)["location"]) for ip in
                                                        ips[1:]]))
    except:
        return None


def get_distance_in_km(server1, server2):
    if server1.get("location", None) is not None and server2.get("location", None) is not None:
        return haversine(server1["location"], server2["location"])
    else:
        raise MissingDataError()


def fall_back_own_ip():
    external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
    return external_ip


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='resolve a domain with a list of dns servers, \
                     and computer the distance between the DNS server\
                     and the resolved server')
    parser.add_argument('-s', '--dns_servers', nargs='+', help='a list of dns servers to compute from', default=None)
    parser.add_argument('--target', '-t', default="md1.libe.com",
                        help='the domain name to resolve or URL of video provider to resolve')
    parser.add_argument('--timeout', default=5, type=float,
                        help='Timeout for the DNS queries')
    parser.add_argument('-c', '--countries', nargs='+', help='a list of countries to select the DNS from', default=None)
    parser.add_argument('--dns-list', help='list of dns to use e.g. americas, eu, asia, world', default="world")

    parser.add_argument('--limit', default=3, type=int,
                        help='Maximum number of dns servers to query')
    parser.add_argument('--use_bind9', action='store_true',
                        help='use bind9 to change DNS resolver')
    parser.add_argument('--list-countries', action='store_true',
                        help='use bind9 to change DNS resolver')
    parser.add_argument('--output-format', default="plain",
                        help='format of the output, one of "plain, simple, grid, fancy_grid, pipe, orgtbl, jira, psql, rst, mediawiki, moinmoin, html, latex, latex_booktabs, textile"')
    parser.add_argument('-output-file', help="name of the file where to write output",
                        default="./res/output")

    args = parser.parse_args()

    myip = fall_back_own_ip()

    client_infos = extract_geoloc_data(myip)

    dns_db_path = "db/nameservers_%s.csv" % args.dns_list

    if args.list_countries is True:
        with open(dns_db_path, "r") as f:
            # print(" ".join(["%s(%3d)" % (k, v) for k, v insorted(Counter(line[2] for line in list(csv.reader(f))).items(), key=lambda x: -x[1])]))
            print(" ".join(sorted({line[2] for line in list(csv.reader(f))})))
            exit(0)

    target = args.target

    # if we require a specific list of countries
    if args.countries is not None:
        dnsips = [ipdata for country in args.countries for ipdata in
                  get_dns_ip_by_country(country, dns_db_path)[:args.limit]]
    else:
        # if we didn't specifies a target dns_server to test
        if args.dns_servers is None:
            with open(dns_db_path) as f:
                reader = csv.reader(f)
                data = list(reader)
                random.shuffle(data)
                dnsips = data[:args.limit]

        else:
            # take all the dns server we have
            dnsips = args.dns_servers[:args.limit]

    reader = geolite2.reader()

    if args.use_bind9:
        update_bind9_dns("8.8.8.8")

    # get the informations from the dns servers from the csv file or retreive it

    dns_servers_infoss = [extract_geoloc_data(dnsip) for dnsip in
                          dnsips if isinstance(dnsip, str)] + [extract_geoloc_data_from_csv_line(dnsip) for dnsip in
                                                               dnsips if isinstance(dnsip, list)]

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

            # resolved_infos = extract_geoloc_data_db(resolved_ips[0])
            # resolved_infos = min([candiate_info for candiate_info in[extract_geoloc_data(resolved_ip) for resolved_ip in resolved_ips]],key=lambda x: get_distance_in_km(my_data, x))
            for resolved_info_index, resolved_infos in enumerate([candiate_info for candiate_info in
                                                                  [extract_geoloc_data(resolved_ip,
                                                                                       resolved_target) for
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
                    "route_to_content": get_route_to(resolved_infos["ip"])
                })

        except (dns.exception.Timeout, MissingDataError)  as e:
            logging.error(e)
            print(e)
            continue

    if len(distance_content_mes) > 0 and len(distance_content_dnss) > 0:
        avg_distance_dns = sum(distance_content_dnss) / len(distance_content_dnss)
        avg_distance_me = sum(distance_content_mes) / len(distance_content_mes)

        avg_distance_dns = str(int(avg_distance_dns)) if avg_distance_dns is not None else "N/A"
        avg_distance_me = str(int(avg_distance_me)) if avg_distance_me is not None else "N/A"
    else:
        avg_distance_dns = "N/A"
        avg_distance_me = "N/A"

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
        "cont_hst": "",
        "route_to_content": "",

    })
    write_output(data, args.output_file, args.output_format)
