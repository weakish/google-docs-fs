#!/usr/bin/env python
#
#       INSTALL.py
#
#       Copyright 2009 Scott Walton <d38dm8nw81k1ng@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; version 2.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

## A Simple installation script. It's not nice, nor particularly good
## but it installs the file system adequately and generates a remove
## script to simplify removal of the file system
import sys
import os

def main():
    if len(sys.argv) == 1:
        python_version = "2.5"
    elif len(sys.argv) == 2:
        python_version = sys.argv[1]
    else:
        print "Usage: INSTALL.py"
        print "or"
        print "INSTALL.py python_version"
        sys.exit(1)
    if python_version == "2.6":
        install_path = "/usr/lib/python2.6/dist-packages/google-docs-fs"
        print "Using Python 2.6! Please read the instructions for ensuring"
        print "compatibility with the GData Python Client"
        if not os.path.isdir('/usr/lib/python2.6/dist-packages/gdata'):
            os.system('./py-2.6.sh')
    else:
        install_path = "/usr/lib/python%s/site-packages/google-docs-fs" % (python_version, )
    print "Installing google-docs-fs to:", install_path
    if not os.path.exists(install_path):
        os.mkdir(install_path)
    for lib in ('gFile.py','gNet.py'):
        infile = open('./%s' % (lib, ))
        outfile = open('%s/%s' % (install_path, lib), 'w')
        outfile.write(infile.read())
        infile.close()
        outfile.close()
    
    ##Install gumount
    infile = open('./gumount')
    outfile = open('/usr/bin/gumount', 'w')
    outfile.write(infile.read())
    infile.close()
    outfile.close()
    
    ##Install gmount
    gmount = """#!/bin/bash

if [ $# -ne 2 ]
	then
	echo "Usage: gmount [mountpoint] [googlemail]"
else
	%s/gFile.py $2 $1
         
fi

## Create the temporary directory 
mkdir -p ~/.google-docs-fs""" % (install_path, )

    f = open('/usr/bin/gmount', 'w')
    f.write(gmount)
    f.close()

    
    ## Create uninstall script
    uninstall = """#!/bin/sh
rm /usr/bin/gmount /usr/bin/gumount
rm -r %s
rm ./REMOVE""" % (install_path, )

    f = open('./REMOVE', 'w')
    f.write(uninstall)
    f.close()

    ## Set files to be executable
    for file in ('/usr/bin/gmount', '/usr/bin/gumount', install_path + '/gFile.py', './REMOVE'):
        os.chmod(file, 0755)
    
    return 0

if __name__ == '__main__': main()
