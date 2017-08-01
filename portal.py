#! /usr/bin/env python3
import argparse
import collections
import glob
import os

import jinja2

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='create data portal')
    parser.add_argument('apath', metavar='N', type=str, nargs='?', default="res/",
                        help='path of the database')

    args = parser.parse_args()

    with open(os.path.join(TEMPLATE_PATH, "portal.html.tpl"), "r") as f:
        t = jinja2.Template(f.read())

    os.chdir(args.apath)

    data_dict = collections.defaultdict(lambda: [])
    data = sorted([outputs.split("/", 1) for outputs in glob.glob("*/*/output.html")],
                  key=lambda x: "".join(x))
    for item in data:
        name = item[1].split("/")[0].split("_")[0]
        path = os.path.join(item[0], item[1])
        data_dict[item[0]].append((name, path))

    print(t.render(data=data_dict))
