from ast import literal_eval
import functools
import json

import requests
from geolite2 import geolite2

from exceptions import MissingDataError

geoloc_data_keys = ['ip', 'city', 'country', 'location', "org"]


def extract_geoloc_data_from_csv_line(data):
    res = dict(zip(geoloc_data_keys, data))
    # convert loc str ==> real array
    if res["location"]!='':
        res["location"] = literal_eval(res["location"])
    else:
        del res["location"]

    return res

@functools.lru_cache(maxsize=-1)
def extract_geoloc_data_ipinfo(ip):
    try:
        response = requests.get("http://ipinfo.io/%s" % (ip))
        if response.ok:

            ipinfo_res = response.json()
            if 'error' in ipinfo_res.keys():
                raise MissingDataError("ipinfo.io returned an error")

            else:
                ip = ipinfo_res.get("ip", "N/A")
                asn = ipinfo_res.get("org", "N/A")
                city = ipinfo_res.get("city", "N/A")
                country = ipinfo_res.get("country", "N/A")
                if ipinfo_res.get("loc", None) is not None:
                    location = list(map(lambda x: float(x), ipinfo_res["loc"].split(",")))
                else:
                    location = None

            res = zip(geoloc_data_keys, [ip, city, country, location, asn])
        else:
            res = zip(geoloc_data_keys, [ip, None, None, None, "N/A"])
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        res = zip(geoloc_data_keys, [ip, None, None, None, "N/A"])

    return dict(res)


@functools.lru_cache(maxsize=-1)
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
