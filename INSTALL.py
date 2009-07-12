#!/usr/bin/env python
#
#       INSTALL.py
#
#       Copyright 2009 Scott Walton <d38dm8nw81k1ng@gmail.com>
#       Mac Compatibility provided by Ben Samuel
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

## A Simple installation script. Creates a REMOVE script to
## assist uninstall.
import sys
import os
from distutils.sysconfig import get_python_lib

def main():
    if len(sys.argv) != 1:
        print "Too many arguments!"
        sys.exit()
    else:
        install_path = os.path.join(get_python_lib(), "google-docs-fs")
    
    
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
    infile = open('./gmount')
    gmount = ''
    for line in infile:
        if './gFile.py $*' in line:
            gmount += '\t%s/gFile.py $*\n' % (install_path, )
        else:
            gmount += line
    outfile = open('/usr/bin/gmount', 'w')
    outfile.write(gmount)
    outfile.close()

    
    ## Create uninstall script
    uninstall = "#!/bin/sh\n" + \
    'rm /usr/bin/gmount /usr/bin/gumount\n' + \
    'rm -r %s\nrm ./REMOVE' % (install_path, )

    f = open('./REMOVE', 'w')
    f.write(uninstall)
    f.close()

    ## Set files to be executable
    for file in ('/usr/bin/gmount', '/usr/bin/gumount', install_path + '/gFile.py', './REMOVE'):
        os.chmod(file, 0755)
    
    return 0

if __name__ == '__main__': main()
