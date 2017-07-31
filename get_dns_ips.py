#! /usr/bin/env python3

import argparse
import random
import json
import requests

if __name__ == "__main__":

    EU28 = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT",
            "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "GB"]

    ASIA = ["AF", "AM", "AZ", "BH", "BD", "BT", "BN", "KH", "CN", "CX", "CC", "IO", "GE", "HK", "IN", "ID", "IR", "IQ",
            "IL", "JP", "JO", "KZ", "KW", "KG", "LA", "LB", "MO", "MY", "MV", "MN", "MM", "NP", "KP", "OM", "PK", "PS",
            "PH", "QA", "SA", "SG", "KR", "LK", "SY", "TW", "TJ", "TH", "TR", "TM", "AE", "UZ", "VN", "YE"]

    AMERICAS = ["AR", "BO", "BR", "CL", "CO", "EC", "FK", "GF", "GY", "GY", "PY", "PE", "SR", "UY", "VE"]

    template_url = "https://public-dns.info/nameserver/%s.json"

    parser = argparse.ArgumentParser(
        description='get a list of DNS countries from https://public-dns.info')
    parser.add_argument('-c', '--countries', nargs='+', help='list of countries to download', default=EU28)
    parser.add_argument('-n', default=1, type=int, help='number of dns servers per countries')
    parser.add_argument('-o', default="db/nameservers.txt", type=str, help='where to store the results')

    args = parser.parse_args()

    res = {}
    for country in args.countries:
        try:
            entries = list(filter(lambda x: x["reliability"] == 1 and ":" not in x["ip"],
                                  requests.get(template_url % country.lower()).json()))
        except json.decoder.JSONDecodeError:
            continue
        if len(entries) == 0:
            continue
        entry = random.choice(entries)
        res[country] = entry["ip"]
        print("%s" % entry["ip"])

    with open(args.o, "w") as f:
        for ip in res.values():
            f.write(ip + "\n")
