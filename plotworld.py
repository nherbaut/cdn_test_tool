import ast
import csv
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

parser = argparse.ArgumentParser(
        description='resolve a domain with a list of dns servers, and computer the distance between the DNS server and the resolved server')
parser.add_argument('-o', help='name of the map for eps export', default="output")


args = parser.parse_args()

me_lats, me_lons = None, None
dns_lats = []
dns_lons = []
content_lats = []
content_lons = []
with open("output.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        lon, lat = ast.literal_eval(row["dns_loc"])
        dns_lats.append(lat)
        dns_lons.append(lon)

        lon, lat = ast.literal_eval(row["content_loc"])
        content_lats.append(lat)
        content_lons.append(lon)

        lon, lat = ast.literal_eval(row["me_loc"])
        me_lats, me_lons = lat, lon





        # draw map with markers for float locations
m = Basemap(projection='hammer', lon_0=0, resolution='c')

m.drawmapboundary(fill_color='#99ffff')
m.fillcontinents(color='#cc9966', lake_color='#99ffff')

x, y = m(me_lats, me_lons)
m.scatter(x, y, 100, marker='o', color='k', zorder=100)
x, y = m(dns_lats, dns_lons)
m.scatter(x, y, 50, marker='o', color='g', zorder=50)
x, y = m(content_lats, content_lons)
m.scatter(x, y, 70, marker='o', color='r', zorder=70)

x0, y0 = m(me_lats, me_lons)
for lat, lon in zip(dns_lats, dns_lons):
    x, y = m(lat, lon)
    m.plot([x, x0], [y, y0], zorder=10, color='k', linestyle="dashed")

for lat0, lon0, lat1, lon1 in zip(content_lats, content_lons,dns_lats,dns_lons):
    (x0, y0), (x1, y1) = m(lat0, lon0), m(lat1, lon1)
    m.plot([x0, x1], [y0, y1], zorder=10, color='g', linestyle="dashed")

plt.show()
plt.savefig('%s.eps'%args.o , format='eps', dpi=1000)