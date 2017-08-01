#! /usr/bin/env python3
import sys
import tabulate
from urllib.parse import urlparse

from geoloc import google_hack, extract_geoloc_data_ipinfo, decypher_host

if __name__ == "__main__":
    for line in sys.stdin:
        netloc = urlparse(line).netloc
        if netloc == '':
            netloc = urlparse(line).path

        data=extract_geoloc_data_ipinfo("",netloc)
        data["target"]=netloc
        data["target_clear"]=decypher_host(netloc)
        sys.stdout.write(tabulate.tabulate([data],headers="keys",tablefmt="fancy_grid")+"\n")


