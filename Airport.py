"""
Airport ID 	Unique OpenFlights identifier for this airport.
Name 		Name of airport. May or may not contain the City name.
City 		Main city served by airport. May be spelled differently from Name.
Country 	Country or territory where airport is located.
IATA/FAA 	3-letter FAA code, for airports located in Country "United States of America".
		3-letter IATA code, for all other airports.
		Blank if not assigned.
ICAO 		4-letter ICAO code.
		Blank if not assigned.
Latitude 	Decimal degrees, usually to six significant digits. Negative is South, positive is North.
Longitude 	Decimal degrees, usually to six significant digits. Negative is West, positive is East.
Altitude 	In feet.
Timezone 	Hours offset from UTC. Fractional hours are expressed as decimals, eg. India is 5.5.
DST 		Daylight savings time. One of E (Europe), A (US/Canada), S (South America), O (Australia), Z (New Zealand), N (None) or U (Unknown). See also: Help: Time
"""

import re


def findAirportNameByIATA(code):
    res = []
    data = open("db/airports.dat", "r")
    for line in data:
        temp = line.split(',')
        if re.search(code, temp[4]):
            res.append(temp[1])
    return res


def findAirportByCity(city):
    res = []
    data = open("db/airports.dat", "r")
    for line in data:
        temp = line.split(',')
        if re.search(city, temp[2]):
            res.append(temp[1])
    return res


def findCountryOfAirportByIATA(code):
    res = []
    data = open("db/airports.dat", "r")
    for line in data:
        temp = line.split(',')
        if re.search(code, temp[4]):
            res.append(temp[3].strip('"'))
    return res


import functools


@functools.lru_cache(maxsize=-1)
def findAllByIATA(code):
    res = []
    import csv
    with open("db/airports.dat", "r") as f:
        reader = csv.reader(f)
        for line in reader:
            if re.search(code, line[4]):
                return line
    return "N/A"
