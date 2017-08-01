#! /usr/bin/env python3
import sys
from urllib.parse import urlparse

import tabulate

from google import google_hack, decypher_google_host

if __name__ == "__main__":
    geoloc_data_keys = ['ip', 'city', 'country', 'location', "org"]

    for line in sys.stdin:
        netloc = urlparse(line).netloc
        if netloc == '':
            netloc = urlparse(line).path

        data = google_hack(netloc, "")
        data = dict(zip(geoloc_data_keys, data))
        data["target"] = netloc
        data["target_clear"] = decypher_google_host(netloc)
        sys.stdout.write(tabulate.tabulate([data], headers="keys", tablefmt="fancy_grid") + "\n")
