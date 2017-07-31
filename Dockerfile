from python:3.6.2-jessie
RUN apt-get update
RUN apt-get install python-pip --yes
RUN pip install maxminddb-geolite2==2017.404 haversine==0.4.5 dnspython==1.15.0
RUN pip install requests
RUN apt-get install dnsutils --yes
RUN pip install youtube-dl jinja2
RUN apt-get install bind9 bind9utils vim --yes
RUN pip install tabulate matplotlib
RUN apt-get install libgeos-dev wget zip --yes
RUN wget https://github.com/matplotlib/basemap/archive/v1.1.0.zip
RUN unzip v1.1.0.zip
WORKDIR /basemap-1.1.0
RUN python ./setup.py install
RUN pip install pyproj scapy-python3
RUN echo "nameserver 127.0.0.1" > /etc/resolv.conf
RUN echo "#!/usr/bin/env bash \n cd /root \n ./dns_handler.py -s 8.8.8.8 \n /root/anycast.py --use_bind9 \"\$@\" " > /root/bootstrap.sh
RUN mkdir -p /root/.config/matplotlib/
RUN echo "backend : Agg" > /root/.config/matplotlib/matplotlibrc
RUN chmod +x /root/bootstrap.sh
RUN mkdir /root/res
COPY db/* /root/db/
COPY data/* /root/data/
COPY templates/* /root/templates/
COPY *.py  /root/
ENTRYPOINT [ "/root/bootstrap.sh" ]
