#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, urllib, sys, os.path, shutil, zipfile, difflib
from math import sqrt

def convertShow(show):
    res = show
    res = res.replace('!','')
    res = res.replace('?','')
    res = res.replace(',',' ')
    p = re.compile('\s+');
    res = p.sub(' ',res)
    res = res.lstrip()
    res = res.rstrip()
    res = res.replace(' ','+')
    return res

def getUrlShow(show,htmlSource):
    list = re.findall('<a href="(/tvshow.*?)">([^<]*)</a>',htmlSource)
    print list

    if len(list) == 1:
        return "http://www.tvsubtitles.net" + list[0][0]
    else:
        matches = []
        for l in list:
            title = l[1]
            title = re.sub("\([0-9]{4}-[0-9]{4}\)","",title)
            title = title.strip()
            matches += [title,]
        print matches
        res = difflib.get_close_matches(show,matches,1)
        if len(res) == 0:
            print "Couldn't find a close match"
            return -1
        else:
            i = 0
            for m in matches:
                if m == res[0]:
                    break
                i = i + 1
            url = "http://www.tvsubtitles.net" + list[i][0]
            print url
            return url
    #p = re.search('<a href="(/tvshow.*?)">',htmlSource)
    #if not p:
    #    print "Can't find the show's subtitle"
    #    return -1
    #return  "http://www.tvsubtitles.net" + p.group(1)

def getShow(show):
    url = "http://www.tvsubtitles.net/search.php?q="+convertShow(show)
    print url
    try:
        htmlSource = urllib.urlopen(url).read()
    except IOError,e:
        print e
        return -1
    res =getUrlShow(show,htmlSource)
    return res

def getEpisodeUrl(htmlSource,season,episode,lang):
    ep = "%(#)02d"% {"#": int(episode)}
    str = season + 'x' + ep
    p = re.search('<td>' + str + '</td>\s<td.*?>.*?</td>\s<td>[0-9]+</td>\s<td><nobr>.*?<a href="([A-Za-z0-9\-\.]*?)"><img src="images/flags/'+lang+'.gif"', htmlSource,re.M) 
    if not p:
        print "Can't find the episode url"
        return -1
    return "http://www.tvsubtitles.net/" + p.group(1)

def getFileUrl(htmlSource):
    p = re.search('<a href="(.*?)"><nobr><h3.*?><img src="images/down.png" ', htmlSource)
    if not p:
        print "Can't find the file url"
        return -1
    return "http://www.tvsubtitles.net/" + p.group(1)

def extractFile(url,rep):
    print url
    zipFile = urllib.urlopen(url).read()
    fout = open(rep+'tmp.zip', "wb")
    fout.write(zipFile)
    fout.close()
    zip = zipfile.ZipFile(rep + 'tmp.zip','r')
    info = zip.infolist()
    if len(info) > 1:
        print "Warning : too many files in the archive.Extracting the first one"
    info = info[0]
    zip.extract(info,rep)
    zip.close()
    os.remove(rep + 'tmp.zip')
    return rep + info.filename

def detectNbSubtitle(season,episode,htmlSource,tag,HD):
    p = re.search('<a href="(.*?)"><nobr><h3.*?><img src="images/down.png" ', htmlSource)
    if p:
        return 1
    p = re.search('<b>Subtitles for this episode:</b>(.*?)Back to',htmlSource, re.DOTALL)
    if not p:
        print "Can't find the section with link"
        return -1
    res = p.group(1)
    ep = "%(#)02d"% {"#": int(episode)}
    str = season + 'x' + ep
    listShow = re.findall('<h5 .*?><img .*?>(.*?'+ep+'.*?)</h5>',res)
    print "List of subs : "
    print listShow
    urlShow = re.findall('<a href="(.*?)"',res);
    urlShow = urlShow[:-1]
    print "URLs :"
    print urlShow
    dlShow = re.findall('<img src="images/downloads.png" .*?>\s*([0-9]+)\s*</p>',res,re.M)
    print "Number of dl :"
    print dlShow
    scoreShow = re.findall('<span style="color:red">([0-9]+)</span>/<span style="color:green">([0-9]+)</span>',res)
    print "Score (b / g) : "
    print scoreShow
    
    if len(listShow) == 0:
        print 'No subtitle found'
        return -1

    print len(listShow)
    print len(urlShow)
    print len(dlShow)
    print len(scoreShow)
    if not (len(listShow) == len(urlShow) and len(urlShow) == len(dlShow) and len(dlShow) == len(scoreShow)):
        print "Size mismatch"
        return -1
    # Look how many match we got per tag
    hd = ((HD == 1) or (isHD(tag) == 1))
    match = []
    max = -1
    idxMax = []
    for l in listShow:
        s = 0
        for t in tag:
            if re.search(t,l,re.I):
                s = s + 1
        match.append(s)
        if hd and not isHD([l]):
            continue
        elif isHD([l]) and not hd:
            continue

        if max < s:
            max = s
            idxMax = [len(match) - 1]
        elif max == s:
            idxMax.append(len(match) - 1)
    if len(idxMax) == 0:
        print "Error finding the max"
        return -1
    elif len(idxMax) == 1:
        return  "http://www.tvsubtitles.net/" + urlShow[idxMax[0]]
    else:
        ratio = []
        idxMaxR = []
        max = -0.1
        for i in idxMax:
            b = int(scoreShow[i][0])
            g = int(scoreShow[i][1])
            if b == 0 and g == 0:
                r = -1
            else:
                r = g / sqrt(b*b+g*g)
            ratio.append(r)
            if r > max:
                max = r
                idxMaxR = [len(ratio) - 1]
            elif r == max:
                idxMaxR.append(len(ratio) - 1)
        if len(idxMaxR) == 0:
            print "Error while comparing ration, choosing the first"
            return "http://www.tvsubtitles.net/" + urlShow[idxMax[0]]
        elif len(idxMaxR) == 1:
            return "http://www.tvsubtitles.net/" + urlShow[idxMaxR[0]]
        else:
            #Comparison on the number of dl
            idxMaxDL = []
            max = 0
            nbDL = []
            for i in idxMaxR:
                dl = int(dlShow[i])
                nbDL.append(dl)
                if dl > max:
                    dl = max
                    idxMaxDL = [len(nbDL)-1]
                elif dl == max:
                    idxMaxDL.append(len(nbDL)-1)
            if (len(idxMaxDL) == 0):
                print "Error while comparing the number of dl, choosing the first"
                return  "http://www.tvsubtitles.net/" + urlShow[idxMaxR[0]]
            elif (len(idxMaxDL) == 1):
                return "http://www.tvsubtitles.net/" + urlShow[idxMaxDL[0]]
            else:
                print "I have no idea how to choose...Let's take the first!"
                return "http://www.tvsubtitles.net/" + urlShow[idxMaxDL[0]]
    return -1

def isHD(tag):
    tagHD = ['720p','1080']
    for t in tag:
        for r in tagHD:
            if re.search(r,t,re.I):
                return 1
    return 0

def getSubtitle(show,season,ep,lang,rep,tag,HD):
    url = getShow(show)
    if url == -1:
        return -1
    #p = re.compile('-[0-9]*\.html')
    #url = p.sub('-'+season+'.html',url)
    url = url.replace(".html",'-'+season+'.html')
    print url;
    htmlSource = urllib.urlopen(url).read()
    url = getEpisodeUrl(htmlSource,season,ep,lang)
    if url == -1:
        return -1
    htmlSource = urllib.urlopen(url).read()
    #Check if we only have one subtitles or two
    res = detectNbSubtitle(season,ep,htmlSource,tag,HD)
    print res
    if res == -1:
        return -1
    elif not res == 1:
        htmlSource = urllib.urlopen(res).read()

    url = getFileUrl(htmlSource)
    if url == -1:
        return -1
    return extractFile(url,rep)

#show = sys.argv[1]
#season = sys.argv[2]
#ep = sys.argv[3]
#lang = sys.argv[4]
#print getSubtitle(show,season,ep,lang)
