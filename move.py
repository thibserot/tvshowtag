#! /usr/bin/python

import sys, subprocess
import syslog

id = sys.argv[1]
file = sys.argv[2]
folder = sys.argv[3]

syslog.syslog("Deluge moving script")
for arg in sys.argv:
    syslog.syslog(arg)
f = open("/home/thibanir/move.log","a")
g = open("/home/thibanir/move.err","a")
p = subprocess.Popen(["/home/thibanir/Project/tvshowtag/serie.py",folder + "/" + file],stdout=f,stderr=g)
p.wait()
f.flush()
f.close()

g.flush()
g.close()

