import urllib.request
import xml.etree.ElementTree as ET
import downloader as tumblr
import concurrent.futures
import re, os, indexer

__author__ = 'LittleLight'

'''
Functions
'''
def download_worker(namespace, directory, post, num, posts_count):
   post_num = num+1

   print("Processing post {0} of {1} ...".format(post_num, posts_count))

   post_url = post.find(".//"+namespace+"loc").text.strip()
   post_date = post.find(".//"+namespace+"lastmod").text.strip()
   post_date = post_date.replace("T","_").replace("Z","")

   tumblr.download(os.path.join(directory,"post{0}".format(post_num)),post_url,post_date)

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

sitemap_url = url+"sitemap1.xml"

sitemap_xml = ""

print("Fetching sitemap file: "+sitemap_url+" ...")
with urllib.request.urlopen(sitemap_url) as response:
   sitemap_xml = response.read().decode("utf-8")

posts = ET.fromstring(sitemap_xml)
namespace = re.match(u"({.*})\w+$", posts.tag).group(1)

posts_count = len(posts)


#Start downloading
with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
    for post,num in zip(posts,range(posts_count)):
            executor.submit(download_worker, namespace, directory, post, num, posts_count)


#Create index
print("Building index.hml ...")
indexer.build(directory, blog)

print("Backup completed!")
