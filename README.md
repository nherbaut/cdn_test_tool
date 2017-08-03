# Presentation #

This tool studies the relation between content ip, dns ip and client ip. It generates output as HTML, Latex and world map graphics

# Docker #

Run this tool as a docker container

```
docker pull nherbaut/cdn_test_tool
```

# Results examples #

[Showcase of the tool on my website][http://data.nextnet.top/cdn]

# Usage # 

```
usage: [-h] [-s DNS_SERVERS [DNS_SERVERS ...]] [--target TARGET]
                  [--timeout TIMEOUT] [-c COUNTRIES [COUNTRIES ...]]
                  [--dns-list DNS_LIST] [--limit LIMIT] 
                  [--list-countries]
                  

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
  --dns-list DNS_LIST   list of dns to use e.g. americas, eu, asia, world
  --limit LIMIT         Maximum number of dns servers to query
  --list-countries      use bind9 to change DNS resolver

```


# Example #

```
docker run -v $PWD/output:/root/res  /nherbaut/cdn_test_tool -c FR DK US CA GB IT -t a0.muscache.com
```

check of IPs with DNS in these countries FR DK US CA GB IT to see what is the resolved content server IP for a0.muscache.com.
HTML repport and images are generated in the output folder


