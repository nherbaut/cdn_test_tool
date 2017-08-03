#! /usr/bin/env python3

import argparse
import json
import random

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
    parser.add_argument('db_path', nargs="?", type=str, help='where to store the results', default=None)

    args = parser.parse_args()


    res = []
    for country in args.countries:
        try:
            entries = list(filter(lambda x: x["reliability"] == 1 and ":" not in x["ip"],
                                  requests.get(template_url % country.lower()).json()))
        except json.decoder.JSONDecodeError:
            continue
        if len(entries) == 0:
            continue
        random.shuffle(entries)
        res += entries[:args.n]
        if args.db_path is None:
            for e in entries[:args.n]:
                print(e["ip"])

    if args.db_path is not None:
        with open(args.db_path, "w") as f:
            for entry in res:
                f.write(entry["ip"] + "\n")
