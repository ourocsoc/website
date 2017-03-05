#!/usr/bin/env python

"""
SSH Stuff
"""

from subprocess import call
import os


HOST = "linux.ox.ac.uk"
PORT = 22
USER = "rocketry"
OUTDIR = "build/"
DEVMODE = False


if not os.path.exists(OUTDIR):
	print ("Nothing to transfer! You should probably build using build.py first!")
	exit(1)
cmd = "scp -2 -r %s%s %s@%s:~/public_html/" % (OUTDIR, '' if DEVMODE else '*', USER , HOST)
print(cmd)
call(cmd, shell=True)
    
