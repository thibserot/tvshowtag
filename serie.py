#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, urllib, sys, os.path, shutil, subtitles, subtitles2

def rename(film = "",lang="en",format="%showname %seasonx%epnumber %eptitle", OUTPUTDIR="/media/ddata/serie/"):
    if film == "":
        print "No movie specified...Exiting"
        return
    film = urllib.unquote(film)
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
    #p = re.search("(.*?)[^0-9]([0-9]{1,2})[A-Za-z\. ]{1,2}([0-9]{1,2})(.*)"+ext,f)
    #WARNING : Experimental
    p = re.search("(.*?[0-9]{4}.*?)[Ss]{0,1}([0-9]{1,2})[eExX\. ]{1,2}([0-9]{1,2})(.*)"+ext,f)
    if not p:
        p = re.search("(.*?)[Ss]{0,1}([0-9]{1,2})[eExX\. ]{1,2}([0-9]{1,2})(.*)"+ext,f)
        if not p:
            print "Can't parse the filename"
            return
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
    title = title.replace("?"," ")
    title = title.replace(","," ")
    title = title.replace(";"," ")
    title = title.replace("&","and")
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
            url_alt = url[:-2] + "_US"
            print "Trying with ",url_alt
            htmlSource = urllib.urlopen(url_alt).read()
            if re.search("HTTP Error 404",htmlSource):
                url_alt = url[:-2]
                print "Trying with ",url_alt
                htmlSource = urllib.urlopen(url_alt).read()
                if re.search("HTTP Error 404",htmlSource):
                    return
            print show
        else:
            return
    
    p = re.search("<title>(.*?)\(a Titles.*?Air Dates Guide\)</title>",htmlSource)
    if not p:
        print "Can't find the title"
    else:
        title = p.group(1)
        title = title.lstrip();
        title = title.rstrip();
    
    #p = re.search(season + "-" + ep1 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
    p = re.search(season + "-" + ep1 + "[^<>]*<a href='[^']{1,}'[^>]*>([^<]*?)</a>",htmlSource)
    if not p:
        #p = re.search(season + "-" + ep2 + ".*<a href='[\[\]A-Za-z0-9\/\._\-:]{1,}'>([a-zA-Z0-9\*\&#\(\)\. ,\-_\?!'\"]*?)</a>",htmlSource)
        p = re.search(season + "-" + ep2 + "[^<>]*<a href='[^']{1,}'[^>]*>([^<]*?)</a>",htmlSource)
        if not p:
            print "Can't find the episode name"
            return
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
    newname = newname.replace(";"," ")
    newname = newname.replace(","," ")
    newname = newname.replace("?"," ")
    newname = newname.replace("!"," ")
    newname = newname.replace(">"," ")
    newname = newname.replace("<"," ")
    p = re.compile('\s+');
    newname = p.sub(' ',newname)
    newname = newname.lstrip();
    newname = newname.rstrip();
    subname = newname + '.srt'
    newname = newname + ext
    
    # Looking for the subtitle file on tvsubtitles
    sub = subtitles.getSubtitle(show,season,ep,lang,rep,tag,HD)
    print sub
    if sub != -1:
        os.rename(sub,rep+subname)
    else:
        sub = subtitles2.getSubtitle(show,season,ep,lang)
        if sub != -1:
            if "Sorry, download limit exceeded" in sub:
                print "Download limit exceeded"
                sub = -1
            else:
                f = open(rep+subname,"w")
                f.write(sub)
                f.close()
    
    print rep + newname
    if os.path.exists(film):
        os.rename(film,rep + newname)
    
    # Copying the rename show on another device (if the path exist)
    print "Checking OUTPUTDIR=",OUTPUTDIR
    if os.path.exists(OUTPUTDIR):
        repout = title + "/Season " + season
        if not os.path.exists(OUTPUTDIR + repout):
            os.makedirs(OUTPUTDIR + repout)
        output = OUTPUTDIR + repout + '/' + newname
        print "output is",output
        sync = "/media/Data/Torrents/sync/"
        if not os.path.exists(output):
            print "Copying file to",output
            shutil.copyfile(rep + newname,output)
            if os.path.exists(sync):
                print "Moving file to",sync
                os.rename(rep + newname,sync + newname)
        if sub != -1:
            output = OUTPUTDIR + repout + '/' + subname
            if not os.path.exists(output):
                print "Copying subtitle file to",output
                shutil.copyfile(rep + subname,output)
                if os.path.exists(sync):
                    print "Moving subtitle file to",sync
                    os.rename(rep + subname,sync + subname)

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
        if (ext in [".avi",".mpg",".mpeg",".mkv",".mp4",".divx",".3gp"]):
            film = dir
            rename(film,lang,format,OUTPUTDIR)

            #f = open("/tmp/test.txt","a")
            #f.write(dir + "\n")
            #f.close()


class WritableObject:
    def __init__(self):
        self.content = []
    def write(self,string):
        self.content.append(string)


#Main
DEBUG = 0

if DEBUG == 1:
    foo = WritableObject()
    sys.stdout = foo


OUTPUTDIR = "/media/Thibanir/Serie/"
OUTPUTDIR = "/home/thibanir/.gvfs/disque\ dur\ on\ freebox/Vidéos/"
OUTPUTDIR = "/media/freebox/TVShows/"
lang = 'en'
format = '%showname %seasonx%epnumber %eptitle'
for arg in sys.argv[1:]:
    renameAll(arg,lang,format,OUTPUTDIR)

if DEBUG == 1:
    f = open("/tmp/tvshowtag.log","w")
    for line in foo.content:
        f.write(line)
    f.close()
