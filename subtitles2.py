#!/usr/bin/python
# -*- coding: utf-8 -*-

import re,difflib,sys
from common import *



#htmlSource = readURL(url)
#f = open("addic7ed.html","w")
#f.write(htmlSource)
#f.close()

def findSerie(showName):

    url = "http://www.addic7ed.com"
    htmlSource = readURL(url)
    #f = open("addic7ed.html","r")
    #htmlSource = f.read()
    #f.close()
    
    p = re.findall("(<select name=\"qsShow\".*?</select>)",htmlSource,re.DOTALL)
    
    if len(p) != 1:
        print "Error more than one select found!!!"
        sys.exit()
    
    series = p[0]
    #print series
    series = re.findall("<option value=\"(\d+)\"[^>]*>([^<]*)</option>",series)
    matches = []
    serieDict = {}
    for serie in series:
        [id,name] = serie
        serieDict[name] = id
        matches += [name,]
    #print len(series)
    res = difflib.get_close_matches(showName,matches,1)
    if len(res) == 1:
        match = res[0]
    else:
        print "couldn't find the TV Show's name"
        return -1
    print match
    id = serieDict[match]
    print id

    return id

def findEpisode(idSerie,seasonNb,epNb,language):
    url = "http://www.addic7ed.com/show/" + idSerie
    htmlSource = readURL(url)
    #f = open("addict7dSeason.html","w")
    #f.write(htmlSource)
    #f.close()
    #f = open("addict7dSeason.html","r")
    #htmlSource = f.read()
    #f.close()
    languageSelected = "English"

    languages = re.search("<select name=\"applang\"(.*?)</select>",htmlSource,re.DOTALL)
    if languages:
        languages = languages.group(1)
        languages = re.findall("<option value=\"([^\"]*)\">([^<]*)</option>",languages)
        #print languages
        for lang in languages:
            if lang[0] == language:
                languageSelected = lang[1]

    seasons = re.findall("<button onmouseup=\"javascript:loadShow\([^,]*?,(\d+)",htmlSource)
    if seasonNb not in seasons:
        print "Wrong season"
        return -1
    else:
        url = "http://www.addic7ed.com/ajax_loadShow.php?show=" + idSerie + "&season=" + seasonNb + "&langs=&hd=&hi="
        htmlSource = readURL(url)
        #f = open("addict7dSeasonCorrect.html","w")
        #f.write(htmlSource)
        #f.close()

    subtitles = re.findall("<tr.*?class=\"epeven completed\"><td>(\d+)</td><td>(\d+)</td><td>.*?</td><td>([^<]*)</td><td class=\"c\">([^<]*?)</td>.*?<td class=\"c\"><a href=\"([^\"]*?)\">Download</a></td>.*?</tr>",htmlSource,re.DOTALL)
    print len(subtitles)
    for subtitle in subtitles:
        [season,ep,lang,tag,link] = subtitle
        if season == seasonNb and ep == epNb and lang.upper() == languageSelected.upper():
            lasturl = url
            url = "http://www.addic7ed.com" + link 
            print "Downloading subtitle in",languageSelected
            srt = readURL(url,lasturl)
            print "Subtitle found"
            return srt
    print "No Subtitle found"
    return -1

def getSubtitle(show,season,ep,lang):
    idSerie = findSerie(show)
    if idSerie == -1:
        print "Couldn't find show name",show
        return -1

    return findEpisode(idSerie,season,ep,lang)


if __name__ == "__main__":
    showName = "30 Rock"
    showSeason = "7"
    showEp = "10"
    lang = "en"
    getSubtitle(showName,showSeason,showEp,lang)
#rep = "./"
#
#idSerie = findSerie(showName)
#srt = findEpisode(idSerie,showSeason,showEp,lang)
#
#if srt != -1:
#    subtitleName = rep + showName + " " + showSeason + "x" + showEp + ".srt"
#    f = open(subtitleName,"w")
#    f.write(srt)
#    f.close()

