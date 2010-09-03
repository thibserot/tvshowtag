#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, urllib, sys, os.path, shutil, subtitles


def usage():
    print "Give the title of a movie and the format"
    print "By default, format = '%showname %seasonx%epnumber %eptitle'"


if len(sys.argv) == 3:
    film = sys.argv[1]
    format = sys.argv[2]
elif len(sys.argv) == 2:
    film = sys.argv[1]
    format = '%showname %seasonx%epnumber %eptitle'
else:
    usage()
    sys.exit()

OUTPUTDIR = "/media/ddata/serie/"
lang = 'en'


idx = film.rfind('/')
if idx != -1:
    f = film[idx+1:]
    rep = film[:idx+1]
else:
    f = film
    rep = ""

idx = film.rfind('.')
if idx != -1:
    ext = film[idx:]
else:
    ext = ""


p = re.search("(.*?).([0-9]{1,2})[A-Za-z\. ]{1,2}([0-9]{1,2})(.*)"+ext,f)
if not p:
    print "Can't parse the filename"
    sys.exit()
title = p.group(1)
season = p.group(2)
ep = p.group(3)
tag = p.group(4)
tag = re.findall('([A-Za-z0-9]+)',tag)
if re.search('\.mkv',ext,re.I):
    HD = 1
else:
    HD = 0

title = title.replace("."," ")
title = title.replace("-"," ")
title = title.replace("_"," ")
title = title.replace("!","")
title = title.replace("(","")
title = title.replace(")","")
title = title.replace("[","")
title = title.replace("]","")
show = title
title = title.replace(" ","")
if title[:3].lower() == "the":
    title = title[3:]

if title[-4:].isdigit() and len(title) > 4 and not title[-5:].isdigit():
    title = title[:-4]+ '_'+title[-4:]

title = title.lstrip();
title = title.rstrip();
print title
season = str(int(season))

ep = int(ep)
ep1 = "%(#)02d"% {"#": ep}
ep2 = "%(#) 2d"% {"#": ep}
ep = str(ep)

print "Title : " + title
print "Season : " + season
print "Ep : " + str(ep)


url = "http://epguides.com/" + title
print url
htmlSource = urllib.urlopen(url).read()


p = re.search("<title>(.*?)\(a Titles.*?Air Dates Guide\)</title>",htmlSource)
if not p:
    print "Can't find the title"
else:
    title = p.group(1)
    title = title.lstrip();
    title = title.rstrip();

#p = re.search(season + "-" + ep1 + ".*<a.*?>(.*?)</a>",htmlSource)
#p = re.search(season + "-" + ep1 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9 ,_\?!'\"]*?)</a>",htmlSource)

#p = re.search(season + "-" + ep1 + ".*<a href='[^<>]{1,}'>(^[<>]*?)</a>",htmlSource)
p = re.search(season + "-" + ep1 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
if not p:
    #p = re.search(season + "-" + ep2 + ".*<a.*?>(.*?)</a>",htmlSource)
    #p = re.search(season + "-" + ep2 + ".*<a href='[[A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9 ,_\?!'\"]*?)</a>",htmlSource)
    #p = re.search(season + "-" + ep2 + ".*<a href='[[A-Za-z0-9\/\._\-:]{1,}'>(^[<>]*?)</a>",htmlSource)
    p = re.search(season + "-" + ep2 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
    if not p:
        print "Can't find the episode name"
        sys.exit()
epname = p.group(1)
newname = format
newname = newname.replace("%showname", title)
newname = newname.replace("%season", season)
newname = newname.replace("%epnumber",ep1)
newname = newname.replace("%eptitle",epname)

newname = newname.replace("*","")
newname = newname.replace("\"","")
newname = newname.replace("/","")
newname = newname.replace("\\","")
newname = newname.replace("[","")
newname = newname.replace("]","")
newname = newname.replace(":"," ")
newname = newname.replace(";"," ")
newname = newname.replace("|","")
newname = newname.replace("=","")
p = re.compile('\s+');
newname = p.sub(' ',newname)
newname = newname.lstrip();
newname = newname.rstrip();
subname = newname + '.srt'
newname = newname + ext

sub = subtitles.getSubtitle(show,season,ep,lang,rep,tag,HD)
if sub != -1:
    os.rename(sub,rep+subname)

print rep + newname
if os.path.exists(film):
    os.rename(film,rep + newname)

if os.path.exists(OUTPUTDIR):
    repout = title + "/Season " + season
    if not os.path.exists(OUTPUTDIR + repout):
        os.makedirs(OUTPUTDIR + repout)
    output = OUTPUTDIR + repout + '/' + newname
    if not os.path.exists(output):
        shutil.copy(rep + newname,output)
