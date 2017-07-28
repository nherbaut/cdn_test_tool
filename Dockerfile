from python:3.6.2-jessie
RUN apt-get update
RUN apt-get install python-pip --yes
RUN pip install maxminddb-geolite2==2017.404 haversine==0.4.5 dnspython==1.15.0
RUN pip install requests
RUN apt-get install dnsutils --yes
RUN pip install youtube-dl jinja2
RUN apt-get install bind9 bind9utils vim --yes
RUN pip install tabulate
RUN echo "#!/usr/bin/env bash \n cd /root \n ./dns_handler.py -s 8.8.8.8 \n /root/anycast.py \"\$@\" " > /root/bootstrap.sh
RUN chmod +x /root/bootstrap.sh
COPY *.csv *.txt /root/
COPY *.tpl /root/
COPY *.py  /root/
ENTRYPOINT [ "/root/bootstrap.sh" ]
