#! /usr/bin/env python3

import argparse
import ast
import csv
import os.path


import numpy as np


def draw_map(input, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    with open(input, "r") as f:
        reader = csv.DictReader(f)

        m = Basemap(projection='hammer', lon_0=0, resolution='c')
        m.drawmapboundary(fill_color='#99ffff')
        m.fillcontinents(color='#cc9966', lake_color='#99ffff')
        data = {}
        for row in reader:
            dns_lon, dns_lat = ast.literal_eval(row["dns_loc"])
            content_lon, content_lat = ast.literal_eval(row["content_loc"])
            me_lon, me_lat = ast.literal_eval(row["me_loc"])
            routes = ast.literal_eval(row["route_to_content"])
            name = " ".join([row["dns_loc"], row["content_loc"], row["me_loc"]])
            data[name] = [(row["dns_ip"], [dns_lon, dns_lat]), (row["cont_ip"], [content_lon, content_lat]),
                          (row["my_ip"], [me_lon, me_lat]), routes]

        cmap = plt.get_cmap('jet')
        names = data.keys()
        colors = dict(zip(names, cmap(np.linspace(0, 1, len(names)))))

        for k, (dns_hop, content_hop, me_hop, routes) in data.items():

            my_lat, my_long = m(me_hop[1][1], me_hop[1][0])
            m.scatter(my_lat, my_long, 100, marker='H', color="black", zorder=120)

            hop1_lat, hop1_long = m(content_hop[1][1], content_hop[1][0], )
            m.scatter(hop1_lat, hop1_long, 30, marker='X', color=colors[k], zorder=100)

            hop1_lat, hop1_long = m(dns_hop[1][1], dns_hop[1][0], )
            m.scatter(hop1_lat, hop1_long, 30, marker='*', color=colors[k], zorder=100)

            m.plot([my_lat, hop1_lat], [my_long, hop1_long], zorder=10, color=colors[k], linestyle="dashed")

            routes = [me_hop] + routes + [content_hop]
            for hop1, hop2 in zip(routes, routes[1:]):
                hop1_lat, hop1_long = m(hop1[1][1], hop1[1][0], )
                hop2_lat, hop2_long = m(hop2[1][1], hop2[1][0], )
                m.scatter(hop2_lat, hop2_long, 10, marker='.', color=colors[k], zorder=100)
                m.plot([hop1_lat, hop2_lat], [hop1_long, hop2_long], zorder=10, color=colors[k], linestyle="solid")






        _, extension = os.path.splitext(output)
        plt.savefig(output, format=extension[1:], dpi=1000)


if __name__ == "__main__":
    import matplotlib
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    parser = argparse.ArgumentParser(
        description='resolve a domain with a list of dns servers, and computer the distance between the DNS server and the resolved server')
    parser.add_argument('-o', help='name of the map for eps export', default="res/output.eps")
    parser.add_argument('-i', help='input file path', default="res/output.csv")
    args = parser.parse_args()
    draw_map(args.i, args.o)
    plt.show()
