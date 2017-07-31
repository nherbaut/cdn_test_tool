# Presentation #

This tool studies the relation between content ip, dns ip and client ip. It generates output as HTML, Latex and world map graphics

# Docker #

Run this tool as a docker container

```
docker pull nherbaut/anycastip
```


# Usage # 

```
usage: anycast.py [-h] [-s DNS_SERVERS [DNS_SERVERS ...]] [--target TARGET]
                  [--timeout TIMEOUT] [-c COUNTRIES [COUNTRIES ...]]
                  [--limit LIMIT] [--use_bind9] [--list-countries]
                  [--output-format OUTPUT_FORMAT] [-dns-db DNS_DB]
                  [-output-file OUTPUT_FILE]

resolve a domain with a list of dns servers, and computer the distance between
the DNS server and the resolved server

optional arguments:
  -h, --help            show this help message and exit
  -s DNS_SERVERS [DNS_SERVERS ...], --dns_servers DNS_SERVERS [DNS_SERVERS ...]
                        a list of dns servers to compute from
  --target TARGET, -t TARGET
                        the domain name to resolve or URL of video provider to
                        resolve
  --timeout TIMEOUT     Timeout for the DNS queries
  -c COUNTRIES [COUNTRIES ...], --countries COUNTRIES [COUNTRIES ...]
                        a list of countries to select the DNS from
  --limit LIMIT         Maximum number of dns servers to query
  --use_bind9           use bind9 to change DNS resolver
  --list-countries      use bind9 to change DNS resolver
  --output-format OUTPUT_FORMAT
                        format of the output, one of "plain, simple, grid,
                        fancy_grid, pipe, orgtbl, jira, psql, rst, mediawiki,
                        moinmoin, html, latex, latex_booktabs, textile"
  -dns-db DNS_DB        name of the dns database file
  -output-file OUTPUT_FILE
                        name of the file where to write output

```


# Examples #

```
docker run --dns=127.0.0.1 -v $PWD/output:/root/res  nherbaut/anycastip -c FR DK US CA GB IT -t a0.muscache.com
```

check of IPs in these countries FR DK US CA GB IT what is the resolved content server IP for a0.muscache.com


