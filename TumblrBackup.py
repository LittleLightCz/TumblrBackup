import urllib.request
import xml.etree.ElementTree as ET
import downloader as tumblr
import concurrent.futures
import re, os, indexer
import requests as req

__author__ = 'LittleLight'

'''
Functions
'''
def download_worker(namespace, directory, post, num, posts_count):
    post_num = num+1

    post_url = post.find(".//"+namespace+"loc").text.strip()
    post_date = post.find(".//"+namespace+"lastmod").text.strip()
    post_date = post_date.replace("T","_").replace("Z","")

    postdir = re.match(r".+/(\d+/.+)$",post_url).group(1).replace("/","_")
    targetdir = os.path.join(directory,postdir)

    print("Processing post into directory: {0}".format(targetdir))

    if not os.path.exists(targetdir):
        tumblr.download(targetdir,post_url,post_date)
    else:
        print("Skipping %s ... directory already exists!" % targetdir)

'''
Configuration
'''

connections = 5

'''
Main script run
'''

print("Enter your blog name:")
blog = input()

directory = blog+"_backup"

print("Creating directory: "+directory+" ...")
if not os.path.exists(directory):
   os.makedirs(directory)

url = "http://{0}.tumblr.com/".format(blog)
print("Your blog URL is: "+url)

resp = req.get(url + "sitemap.xml")
resp.encoding = "UTF-8"

root_sitemap = ET.fromstring(resp.text)
sitemap_urls = (tag[0].text for tag in root_sitemap)
sitemap_urls = [url for url in sitemap_urls if "sitemap-pages.xml" not in url]

with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
    for sitemap_url in sitemap_urls:

        print("Fetching sitemap file: "+sitemap_url+" ...")
        resp = req.get(sitemap_url)
        resp.encoding = "UTF-8"

        sitemap_xml = resp.text

        posts = ET.fromstring(sitemap_xml)
        namespace = re.match(r"({.*})\w+$", posts.tag).group(1)

        posts_count = len(posts)

        #Start downloading
        for post,num in zip(posts,range(posts_count)):
            #redundant check
            post_url = post.find(".//"+namespace+"loc").text.strip()
            if post_url != url:
                executor.submit(download_worker, namespace, directory, post, num, posts_count)


#Create index
print("Building index.hml ...")
indexer.build(directory, blog)

print("Backup completed!")
