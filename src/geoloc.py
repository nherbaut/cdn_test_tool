from ast import literal_eval

import requests
from geolite2 import geolite2
from geopy.geocoders import Nominatim

from Airport import *
from exceptions import MissingDataError
from google import google_hack

DBIP_API_KEY = "029566a24299d02edb24f8ab425456f57f5cd4a4"
geoloc_data_keys = ['ip', 'city', 'country', 'location', "org"]
geolocator = Nominatim()


def extract_geoloc_data(ip, target_hostname=None):
    return extract_geoloc_data_ipinfo(ip, target_hostname)


@functools.lru_cache(maxsize=-1)
def extract_geoloc_data_dbip(ip, target_hostname=None):
    template = "http://api.db-ip.com/v2/%s/%s"
    ipinfo_res = requests.get(template % (DBIP_API_KEY, ip)).json()
    ip = ipinfo_res.get("ipAddress", "N/A")
    asn = ipinfo_res.get("org", "N/A")
    city = ipinfo_res.get("city", "N/A")
    geolocation_retreived = geolocator.geocode(city)

    country = ipinfo_res.get("countryCode", "N/A")
    res = zip(geoloc_data_keys,
              [ip, city, country, [geolocation_retreived.latitude, geolocation_retreived.longitude], asn])
    return dict(res)


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
        res = zip(geoloc_data_keys, google_hack(target_hostname, ip))
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
                sys.stderr("a problem occured when using ipinfo.io service. Make sure you have not exceeded the allowance and try again")
                res = zip(geoloc_data_keys, [ip, None, None, None, "N/A"])
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
            res = zip(geoloc_data_keys, [ip, None, None, None, "N/A"])

    return dict(res)


@functools.lru_cache(maxsize=-1)
def extract_geoloc_data_db(ip, target, georeader=geolite2.reader()):
    data = georeader.get(ip)
    if data is not None:
        city = data["city"]["names"]['en'] if data.get('city', None) is not None else None
        country = data['country']["iso_code"] if data.get('country', None) is not None else None
        location = (data['location']["latitude"], data['location']["longitude"]) if data.get('location',
                                                                                             None) is not None else None
        return {'ip': ip, 'city': city, 'country': country, 'location': location}
    else:
        return {'ip': ip, 'city': None, 'country': None, 'location': None}
