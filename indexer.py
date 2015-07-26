from bs4 import BeautifulSoup
import os

__author__ = 'LittleLight'


def build(targetDir, blog):
    with open(os.path.join(targetDir,"index.html"),"w", encoding="utf-8") as f:
        f.write('<html>')
        f.write('<head>')
        f.write('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">')
        f.write('</head>')
        f.write('<h1>'+blog+' backup</h1>')
        f.write('<body>\n')

        for root, dirs, files in os.walk(targetDir):
            for file in files:
                _process(f, root, file)

        f.write('</body>')
        f.write('</html>')


def _process(f, root, file):
    if file == "post.html":
        f.write('<hr>\n')
        f.write('<div>\n')
        _,post_dir = os.path.split(root)
        file_path = os.path.join(post_dir,file)

        with open(os.path.join(root,file), "r", encoding="utf-8") as post_file:
            content = post_file.read()

            if "<section" in content:
                soup = BeautifulSoup(content, "html.parser")
                for img in soup.findAll("img"):
                    img["src"] = os.path.join(post_dir,img["src"])

                for video in soup.findAll("video"):
                    video["src"] = os.path.join(post_dir,video["src"])

                for frame in soup.findAll("iframe", {"class":"photoset"}):
                    frame["src"] = os.path.join(post_dir,frame["src"])
                    frame["height"] = 800

                f.write(soup.prettify())

            else:
                f.write('<iframe style="width: 90%; height: 1000px;" src="{0}">'.format(file_path))
                f.write('</iframe>\n')
                f.write('</div>\n')
