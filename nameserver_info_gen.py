#! /usr/bin/env python3

import csv

from geoloc import *

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='update nameserver file')
    parser.add_argument('-i', help="input file path containing ips, one per list",
                        default="nameservers.txt")
    parser.add_argument('-o', help="name of the output file to generate",
                        default="nameservers.csv")
    args = parser.parse_args()

    with open(args.i) as f:
        dnsips = f.read().split("\n")

    geoloc_datas = []
    existing_ips = {x[1] for x in [geoloc_data["ip"] for geoloc_data in geoloc_datas]}
    for dnsip in (set(dnsips) - existing_ips):
        if dnsip == '':
            continue
        geoloc_data = extract_geoloc_data_ipinfo(dnsip)
        #geoloc_data = extract_geoloc_data_db(dnsip)
        # geoloc_data["asn"] = extract_geoloc_data_ipinfo(geoloc_data["ip"])["org"]
        geoloc_datas.append(geoloc_data)
        print(geoloc_data)

    with open(args.o, 'w') as csvfile:
        nswriter = csv.writer(csvfile)
        for geoloc_data in geoloc_datas:
            nswriter.writerow(geoloc_data.values())
