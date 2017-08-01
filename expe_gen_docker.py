#! /usr/bin/env python3
import requests
import subprocess

country = requests.get("http://ipinfo.io").json()["country"]
print("#connecting from %s" % country)
print("#pase this to launch the experiment")
tpl = "sudo docker run -d -v $PWD/%s/%s_%s:/root/res  nherbaut/anycastip  -t %s "
data = {"airbnb": "a0.muscache.com",
        "ebay.com": "i.ebayimg.com",
        "www.wikipedia.org": "www.wikipedia.org",
        "www.qq.com": "img1.gtimg.com",
        "reddit.com": "i.redditmedia.com",
        "amazon.com": "images-na.ssl-images-amazon.com",
        "taobao.com": "gw.alicdn.com",
        "twitter.com": "pbs.twimg.com",
        "alibab": "img.alicdn.com",
        "live.com": "auth.gfx.ms",
        "youtube": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "twitch": "https://www.twitch.tv/videos/158047931"}
for k, v in data.items():
    subprocess.call(tpl % (country, k, country, v), shell=True)
