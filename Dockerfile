FROM python:3.6.2-jessie
RUN apt-get update
RUN apt-get install python-pip dnsutils  bind9 bind9utils vim libgeos-dev wget zip --yes
RUN pip install maxminddb-geolite2==2017.404 haversine==0.4.5 dnspython==1.15.0 requests youtube-dl jinja2 tabulate matplotlib pyproj scapy-python3
RUN wget https://github.com/matplotlib/basemap/archive/v1.1.0.zip
RUN unzip v1.1.0.zip
WORKDIR /basemap-1.1.0
RUN python ./setup.py install
RUN echo "nameserver 127.0.0.1" > /etc/resolv.conf
RUN echo "#!/usr/bin/env bash \n cd /root \n ./dns_handler.py -s 8.8.8.8 \n /root/anycast.py --use_bind9 \"\$@\" " > /root/bootstrap.sh
RUN mkdir -p /root/.config/matplotlib/
RUN echo "backend : Agg" > /root/.config/matplotlib/matplotlibrc
RUN chmod +x /root/bootstrap.sh
RUN mkdir /root/res
COPY assets/js /root/assets/js
COPY assets/css /root/assets/js
COPY db/* /root/db/
COPY data/* /root/data/
COPY templates/* /root/templates/
COPY *.py  /root/
ENTRYPOINT [ "/root/bootstrap.sh" ]
