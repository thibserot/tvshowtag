#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2

def readURL(url, lasturl="", encoding=""):
    #opener = urllib2.build_opener()
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    #htmlSource = opener.open(url).read()
    #return htmlSource
    opener = urllib2.build_opener()
    headers = { 'User-agent' : 'Mozilla/5.0' }
    if lasturl != "":
        headers['Referer'] = lasturl
    req =  urllib2.Request(url,"",headers)
    handle = urllib2.urlopen(req)
    htmlSource = handle.read()
    if encoding == "":
        encoding=handle.headers['content-type'].split('charset=')[-1]
    #print "encoding=",encoding
    
    if encoding == "text/html":
        return htmlSource
    try:
        htmlSource = unicode(htmlSource,encoding)
    except UnicodeEncodeError:
        print "unicode error"
        htmlSource = unicode(htmlSource,"latin-1")

    return htmlSource

