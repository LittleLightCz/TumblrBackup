import os
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse as u
import re

__author__ = 'LittleLight'


def _parse(m):
    return u.quote(m.group(0))


def download(targetDir, url, date):
    url = re.sub(r"[^/]+$",_parse,url)
    with urllib.request.urlopen(url) as response:
        soup = BeautifulSoup(response.read().decode("utf-8"), "html.parser")

        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        _process(soup, targetDir)


def _downloadImage(img, targetDir):
    url = img["src"]
    filename = re.match(r".*/([^/]+)$",url).group(1)

    print("Downloading image: "+url)
    urllib.request.urlretrieve(url, os.path.join(targetDir,filename))

    img["src"] = filename


def _getVideoExtension(type):
    return "."+re.match(r".*/([^/]+)$", type).group(1)

def _processVideo(soup, targetDir):
    for video in soup.findAll("video"):
        source = video.find("source")

        url = source["src"]
        filename = re.match(r".*/([^/]+)$",url).group(1)
        filename += _getVideoExtension(source["type"]);

        print("Downloading video: "+url)
        urllib.request.urlretrieve(url, os.path.join(targetDir,filename))

        source["src"] = filename


def _downloadVideos(soup, targetDir):
    _downloadIframes(soup, targetDir, _processVideo, "tumblr_video_iframe")


def _downloadImages(post, targetDir):
    for img in post.findAll("img"):
        _downloadImage(img, targetDir)


def _processPhotoset(soup, targetDir):
    links = soup.findAll("a",{"class":"photoset_photo"})
    for link in links:
        img = link.find("img")
        #replace image's src for the bigger one
        img["src"] = link["href"]
        _downloadImage(img, targetDir)
        link["href"] = img["src"]



def _downloadPhotoset(post, targetDir):
    _downloadIframes(post, targetDir, _processPhotoset, "photoset")


def _downloadIframes(post, targetDir, process, className = None):

    if className:
        frames = post.findAll("iframe", {"class":className})
    else:
        frames = post.findAll("iframe")

    for frame, num in zip(frames,range(len(frames))):
        url = frame["src"]
        frame_name = "frame{0}.html".format(num)

        with urllib.request.urlopen(url) as response:
            soup = BeautifulSoup(response.read().decode("utf-8"), "html.parser")
            process(soup, targetDir)

            with open(os.path.join(targetDir,frame_name),"w", encoding="utf-8") as f:
                f.write(soup.prettify())

        if className == "tumblr_video_iframe":
            _,post_dir = os.path.split(targetDir)
            frame["src"] = os.path.join(post_dir, frame_name)
        else:
            frame["src"] = frame_name



def _downloadMedia(post, targetDir):
    _downloadImages(post, targetDir)
    _downloadPhotoset(post, targetDir)


def _process(soup, targetDir):
    post = soup.find("section", {"class":"post"})

    if post:
        _downloadMedia(post, targetDir)
    else:
        post = soup

    _downloadVideos(soup, targetDir)

    with open(os.path.join(targetDir,"post.html"), "w", encoding="utf-8") as f:
        f.write(post.prettify())

