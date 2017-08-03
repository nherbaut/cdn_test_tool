from Airport import findAllByIATA, get_country_code_by_name


def google_hack(hostname, ip):
    decyphered_hostname = decypher_google_host(hostname)

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
    return [ip, city, get_country_code_by_name(country), [float(lat), float(lon)], org]


def decypher_google_host(hostname):
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
