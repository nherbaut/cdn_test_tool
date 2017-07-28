#! /usr/bin/env python3
from jinja2 import Template
from tabulate import tabulate


def handle_html(data):
    with open("index.html.tpl", "r") as f:
        t = Template(f.read())
        return t.render(table=tabulate(data,tablefmt="html", headers="keys"))
    return "Error"


if __name__=="__main__":
    mock = [{'Index': '01.01', 'dns_ip': '64.6.65.6', 'cont_ip': '77.153.129.113', 'my_ip': '109.15.110.163', 'dns_iso': 'US', 'content_iso': 'FR', 'me_iso': 'FR', 'cnd_count_km': '6543', 'me_count_km': '639', 'dns_as': 'AS36627 VeriSign Global Registry Services', 'cont_as': 'AS15557 Societe Francaise du Radiotelephone S.A.', 'cont_hst': 'r6---sn-n4g-cvqs.googlevideo.com'}, {'Index': 'avg', 'dns_ip': '', 'cont_ip': '', 'my_ip': '', 'dns_iso': '', 'content_iso': '', 'me_iso': '', 'cnd_count_km': '6543', 'me_count_km': '639', 'dns_as': '', 'cont_as': '', 'cont_hst': ''}]
    print(handle_html(data=mock))




