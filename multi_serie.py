#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
from serie import rename



OUTPUTDIR = "/media/ddata/serie/"
lang = 'en'
format = '%showname %seasonx%epnumber %eptitle'

def renameAll(dir):
    #Check if we have a folder
    if os.path.isdir(dir):
        res = os.listdir(dir)
        for r in res:
            renameAll(os.path.join(dir,r))
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

for arg in sys.argv[1:]:
    renameAll(arg)
