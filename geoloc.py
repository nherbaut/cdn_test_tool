import json
from ast import literal_eval

import requests
from geolite2 import geolite2

from Airport import *
from exceptions import MissingDataError

geoloc_data_keys = ['ip', 'city', 'country', 'location', "org"]
with open("db/iso3166-1.json") as f:
    COUNTRIES_CODE = json.loads(f.read())["3166-1"]


@functools.lru_cache()
def get_country_code_by_name(full_name):
    for country in COUNTRIES_CODE:

        if country["name"] == full_name:
            return country["alpha_2"]

    return "N/A"


def decypher_host(hostname):
    google_decode_map = {"0": "u", "1": "z", "2": "p", "3": "k", "4": "f", "5": "a", "6": "5", "7": "0", "8": "v",
                         "9": "q",
                         "a": "l", "b": "g", "c": "b", "d": "6", "e": "1", "f": "w", "g": "r", "h": "m", "i": "h",
                         "j": "c",
                         "k": "7", "l": "2", "m": "x", "n": "s", "o": "n", "p": "i", "q": "d", "r": "8", "s": "3",
                         "t": "y",
                         "u": "t", "v": "o", "w": "j", "x": "e", "y": "9", "z": "4"}

    coded_bit = hostname.split("---")[1].split(".")[0]
    decoded_bit = ""
    for letter in coded_bit:
        if letter in google_decode_map:
            decoded_bit += google_decode_map[letter]
        else:
            decoded_bit += letter
    return decoded_bit


def google_hack(hostname, ip):
    decyphered_hostname = decypher_host(hostname)

    if decyphered_hostname.count("-") == 2:
        org = decyphered_hostname.split("-")[1]
        city = decyphered_hostname.split("-")[2][:3].upper()
    else:
        isp = False
        city = decyphered_hostname.split("-")[1][:3].upper()
        org = None
    # 1264,"Merignac","Bordeaux","France","BOD","LFBD",44.828335,-0.715556,162,1,"E"
    _, _, city, country, code, _, lat, lon, _, _, _ = findAllByIATA(city)
    if org is None:
        org = "Google %s DC" % city
    return zip(geoloc_data_keys, [ip, city, get_country_code_by_name(country), [float(lat), float(lon)], org])


def extract_geoloc_data_from_csv_line(data):
    res = dict(zip(geoloc_data_keys, data))
    # convert loc str ==> real array
    if res["location"] != '':
        res["location"] = literal_eval(res["location"])
    else:
        del res["location"]

    return res


@functools.lru_cache(maxsize=-1)
def extract_geoloc_data_ipinfo(ip, target_hostname=None):
    if target_hostname is not None and "googlevideo.com" in target_hostname:
        res = google_hack(target_hostname, ip)
    else:
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
