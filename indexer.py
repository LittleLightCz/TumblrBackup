import os

__author__ = 'LittleLight'

def build(targetDir):
    with open(os.path.join(targetDir,"index.html"),"w", encoding="utf-8") as f:
        f.write('<html>')
        f.write('<head>')
        f.write('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">')
        f.write('</head>')
        f.write('<body>')
        for root, dirs, files in os.walk(targetDir):
            for file in files:
                _process(f, root, file)

        f.write('</body>')
        f.write('</html>')

def _process(index_f, root, file):
    if file == "post.html":
        _,file_path = os.path.split(root)
        file_path = os.path.join(file_path,file)
        index_f.write('<iframe style="width: 90%; height: 1000px;" src="{0}">'.format(file_path))
        index_f.write('</iframe><br>\n')
