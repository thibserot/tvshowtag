#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, urllib, sys, os.path, shutil, subtitles

def rename(film = "",lang="en",format="%showname %seasonx%epnumber %eptitle", OUTPUTDIR="/media/ddata/serie/"):
    if film == "":
        print "No movie specified...Exiting"
        sys.exit()

    # Extracting the path from the title
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
    
    # Trying to find the tvshow's name, its episode and season
    p = re.search("(.*?)[^0-9]([0-9]{1,2})[A-Za-z\. ]{1,2}([0-9]{1,2})(.*)"+ext,f)
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
    
    # Looking on epguides what's the episode name is
    url = "http://epguides.com/" + title
    print url
    htmlSource = urllib.urlopen(url).read()
    if re.search("HTTP Error 404",htmlSource):
        print "Wrong url"
        if url.upper()[-2:] == "US":
            url = url[:-2] + "_US"
            print "Trying with ",url
            htmlSource = urllib.urlopen(url).read()
            print show
        else:
            sys.exit()
    
    p = re.search("<title>(.*?)\(a Titles.*?Air Dates Guide\)</title>",htmlSource)
    if not p:
        print "Can't find the title"
    else:
        title = p.group(1)
        title = title.lstrip();
        title = title.rstrip();
    
    #p = re.search(season + "-" + ep1 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
    p = re.search(season + "-" + ep1 + "[^<>]*<a href='[^']{1,}'>([^<]*?)</a>",htmlSource)
    if not p:
        #p = re.search(season + "-" + ep2 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
        p = re.search(season + "-" + ep2 + "[^<>]*<a href='[^']{1,}'>([^<]*?)</a>",htmlSource)
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
    
    # Looking for the subtitle file on tvsubtitles
    sub = subtitles.getSubtitle(show,season,ep,lang,rep,tag,HD)
    if sub != -1:
        os.rename(sub,rep+subname)
    
    print rep + newname
    if os.path.exists(film):
        os.rename(film,rep + newname)
    
    # Copying the rename show on another device (if the path exist)
    if os.path.exists(OUTPUTDIR):
        repout = title + "/Season " + season
        if not os.path.exists(OUTPUTDIR + repout):
            os.makedirs(OUTPUTDIR + repout)
        output = OUTPUTDIR + repout + '/' + newname
        if not os.path.exists(output):
            shutil.copy(rep + newname,output)

def renameAll(dir,lang,format,OUTPUTDIR):
    #Check if we have a folder
    if os.path.isdir(dir):
        res = os.listdir(dir)
        for r in res:
            renameAll(os.path.join(dir,r),lang,format,OUTPUTDIR)
    else:
        # Check extension
        ext = os.path.splitext(dir)[1]
        ext = ext.lower()
        if (ext in [".avi",".mpg",".mpeg",".mkv",".mp4",".divx"]):
            film = dir
            rename(film,lang,format,OUTPUTDIR)

            #f = open("/tmp/test.txt","a")
            #f.write(dir + "\n")
            #f.close()


#Main

OUTPUTDIR = "/media/ddata/serie/"
lang = 'en'
format = '%showname %seasonx%epnumber %eptitle'
for arg in sys.argv[1:]:
    renameAll(arg,lang,format,OUTPUTDIR)
            
