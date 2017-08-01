#! /usr/bin/env python3

import argparse
import ast
import csv
import logging
import os.path

import numpy as np


def draw_map(input_csv_path, output_image_path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    if output_image_path is not None:
        factor=0.1
    else:
        factor=1

    with open(input_csv_path, "r") as f:
        reader = csv.DictReader(f)

        data = {}
        for row in reader:
            dns_lon, dns_lat = ast.literal_eval(row["dns_loc"])
            content_lon, content_lat = ast.literal_eval(row["content_loc"])
            me_lon, me_lat = ast.literal_eval(row["me_loc"])
            try:
                routes = ast.literal_eval(row["route_to_content"])
            except SyntaxError:
                routes = []
                logging.error("failed to compute routes for %s " % row["Index"])
            data[row["dns_iso"]] = [(row["dns_ip"], [dns_lon, dns_lat]), (row["cont_ip"], [content_lon, content_lat]),
                                    (row["my_ip"], [me_lon, me_lat]), routes]

        m = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, \
                    llcrnrlon=-180, urcrnrlon=180, lat_ts=20, resolution='c')
        m.drawmapboundary(fill_color='#99ffff')
        m.fillcontinents(color='#cc9966', lake_color='#99ffff')

        cmap = plt.get_cmap('jet')
        names = data.keys()
        colors = dict(zip(names, cmap(np.linspace(0, 1, len(names)))))

        me_hop = list(data.values())[0][2]
        my_lat, my_long = m(me_hop[1][1], me_hop[1][0])
        m.scatter(my_lat, my_long, 30*factor, marker='H', color="black", zorder=120, label="client")

        for k, (dns_hop, content_hop, me_hop, routes) in data.items():

            hop1_lat, hop1_long = m(content_hop[1][1], content_hop[1][0], )
            m.scatter(hop1_lat, hop1_long, 20*factor, marker='o', color=colors[k], zorder=100, label="%s Content" % k)

            hop1_lat, hop1_long = m(dns_hop[1][1], dns_hop[1][0], )
            m.scatter(hop1_lat, hop1_long, 10*factor, marker='^', color=colors[k], zorder=100, label="%s DNS" % k)

            m.plot([my_lat, hop1_lat], [my_long, hop1_long], zorder=3, color=colors[k], linestyle="dashed", lw=1*factor)

            routes = [me_hop] + routes + [content_hop]
            for hop1, hop2 in zip(routes, routes[1:]):
                hop1_lat, hop1_long = m(hop1[1][1], hop1[1][0], )
                hop2_lat, hop2_long = m(hop2[1][1], hop2[1][0], )
                m.scatter(hop2_lat, hop2_long, 10*factor, marker='.', color=colors[k], zorder=110)
                m.plot([hop1_lat, hop2_lat], [hop1_long, hop2_long], lw=3*factor, zorder=110, color=colors[k],
                       linestyle="solid")

        from matplotlib.font_manager import FontProperties


        plt.legend(loc='best',
          fancybox=True, shadow=True, ncol=3,fontsize = 'x-small')
        if output_image_path is not None:
            _, extension = os.path.splitext(output_image_path)
            plt.savefig(output_image_path, format=extension[1:], dpi=1000)
            plt.clf()


if __name__ == "__main__":
    import matplotlib
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap

    parser = argparse.ArgumentParser(
        description='resolve a domain with a list of dns servers, and computer the distance between the DNS server and the resolved server')
    parser.add_argument('-o', help='name of the map for eps export', default=None)
    parser.add_argument('-i', help='input file path', default="res/output.csv")
    args = parser.parse_args()
    draw_map(args.i, args.o)
    if args.o is None:
        plt.show()

