#! /usr/bin/env python3
import csv
import os
import shutil
from datetime import datetime

from jinja2 import Template
from tabulate import tabulate

from plotworld import draw_map


def copy_html_assets(dst):
    if not os.path.exists(os.path.join(dst, "assets")):
        shutil.copytree("assets", os.path.join(dst, "assets"))


def handle_html(data):
    with open("templates/index.html.tpl", "r") as f:
        t = Template(f.read())
        return t.render(table=tabulate(data, tablefmt="html", headers="keys"))


def back_file_if_exist(filepath):
    if os.path.exists(filepath):
        path_fname, extension = os.path.splitext(filepath)
        new_path = path_fname + "." + str(datetime.now()).replace(" ", "_") + extension
        os.rename(filepath, new_path)


def write_output(data, output_file, custom_output_format):
    base_patrh = os.path.dirname(output_file)

    if not os.path.exists(base_patrh):
        os.mkdir(base_patrh)

    for output_format in set(["plain", "latex", "html"] + [custom_output_format]):

        data_pretty = [{k: v for k, v in item.items() if
                        k not in ["Index", "cont_hst", "dns_loc", "content_loc", "me_loc",
                                  "route_to_content"]} for item in data]
        formatted_output_path = "%s.%s" % (output_file, output_format)
        back_file_if_exist(formatted_output_path)
        with open(formatted_output_path, "w") as f:

            if output_format == "html":
                f.write(handle_html(data_pretty))
                copy_html_assets(os.path.join(base_patrh))
            else:
                f.write(tabulate(data_pretty, tablefmt=output_format, headers="keys"))

    # raw data written in csv-file

    raw_output_path = "%s.csv" % output_file
    back_file_if_exist(raw_output_path)
    with open(raw_output_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data[:-1])
    for aformat in ["eps", "png", "svg"]:
        map_output_path = "%s.%s" % (output_file, aformat)
        back_file_if_exist(map_output_path)
        draw_map("%s.csv" % output_file, map_output_path)


if __name__ == "__main__":
    mock = [{'Index': '01.01', 'dns_ip': '64.6.65.6', 'cont_ip': '77.153.129.113', 'my_ip': '109.15.110.163',
             'dns_iso': 'US', 'content_iso': 'FR', 'me_iso': 'FR', 'cnd_count_km': '6543', 'me_count_km': '639',
             'dns_as': 'AS36627 VeriSign Global Registry Services',
             'cont_as': 'AS15557 Societe Francaise du Radiotelephone S.A.',
             'cont_hst': 'r6---sn-n4g-cvqs.googlevideo.com'},
            {'Index': 'avg', 'dns_ip': '', 'cont_ip': '', 'my_ip': '', 'dns_iso': '', 'content_iso': '', 'me_iso': '',
             'cnd_count_km': '6543', 'me_count_km': '639', 'dns_as': '', 'cont_as': '', 'cont_hst': ''}]
    print(handle_html(data=mock))
