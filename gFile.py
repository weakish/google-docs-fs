#!/usr/bin/env python
#
#   gFile.py
#
#   Copyright 2008-2009 Scott Walton <d38dm8nw81k1ng@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License (version 2), as
#   published by the Free Software Foundation
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

import stat
import os
import sys
import errno
import time
import fuse
import gNet

from subprocess import *

fuse.fuse_python_api = (0,2)

class GStat(object):
    """
    The stat class to use for getattr
    """
    def __init__(self):
        """
        Purpose: Sets a default set of file attributes
        Returns: Nothing
        """
        self.st_mode = stat.S_IFDIR | 0744
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_size = 4096
        self.st_atime = int(time.time())
        self.st_mtime = self.st_atime
        self.st_ctime = self.st_atime

class GFile(fuse.Fuse):
    """
    The main Google Docs filesystem class. Most work will be done
    in here.
    """

    def __init__(self, em, pw, *args, **kw):
        """
        Purpose: Connect to the Google Docs Server and verify credentials
        em: User's email address
        pw: User's password
        *args: Args to pass to Fuse
        **kw: Keywords to pass to Fuse
        Returns: Nothing
        """

        fuse.Fuse.__init__(self, *args, **kw)
        self.gn = gNet.GNet(em, pw)
        self.directories = {}
        self.files = {}



    def getattr(self, path):
        """
        Purpose: Get information about a file
        path: String containing relative path to file using mountpoint as /
        Returns: a GStat object with some updated values
        """

        pe = path.split('/')
        self.files[''] = GStat()
        st = self.files[pe[-1]]
        # Set proper attributes for files and directories
        if path == '/': # Root
            pass
        elif pe[-1] in self.directories: # Is a directory
            pass
        elif pe[-1] in self.directories[pe[-2]]: # Is a file
            pass
        else: # Evidently, it must not exist
            return -errno.ENOENT

        return st

    def readdir(self, path, offset):
        """
        Purpose: Give a listing for ls
        path: String containing relative path to file using mountpoint as /
        offset: Included for compatibility. Does nothing
        Returns: Directory listing for ls
        """

        dirents = ['.', '..']
        pe = path.split('/')[1:]

        if path == '/': # Root
            excludes = []
            self.directories[''] = []
            feed = self.gn.get_docs(filetypes = ['folder'])
            for dir in feed.entry:
                excludes.append('-' + dir.title.text.encode('UTF-8'))
                self.directories[dir.title.text.encode('UTF-8')] = []
            if len(excludes) > 0:
                feed = self.gn.get_docs(filetypes = excludes)
                for doc in feed.entry:
                    self.directories[''].append(doc.title.text.encode('UTF-8'))
        else: #Directory
            self.directories[pe[-1]] = []
            feed = self.gn.get_docs(folder = pe[-1])
            for file in feed.entry:
                if file.category[0].label is 'folder':
                    self.directories[file.title.text.encode('UTF-8')]
                self.directories[pe[-1]].append(file.title.text.encode('UTF-8'))

        for entry in self.directories[pe[-1]]:
            dirents.append(entry)

        # Set the appropriate attributes for use with getattr()
        for file in feed.entry:
            self._setattr(file)

        for r in dirents:
            yield fuse.Direntry(r)

    def mknod(self, path, mode, dev):
        pass

    def unlink(self, path):
        """
        Purpose: Remove a file
        path: String containing relative path to file using mountpoint as /
        Returns: 0 to indicate success
        """
        pe = path.split('/')[1:]
        gd_client.erase(pe[-1])
        # TODO: Finish Me!

    def _setattr(self, entry):
        """
        Purpose: Set the getattr information for entry
        entry: DocumentListEntry object to extract data from
        Returns: Nothing
        """
        f = entry.title.text.encode('UTF-8')
        self.files[f] = GStat()
        if entry.category[0].label is 'folder':
            self.files[f].st_mode = stat.S_IFDIR | 0744
            self.files[f].st_nlink = 2
        else:
            self.files[f].st_mode = stat.S_IFREG | 0744
            self.files[f].st_nlink = 1
            self.files[f].st_size = len(f)

        #Set times
        self.files[f].st_atime = int(time.time())
        self.files[f].st_mtime = self._time_convert(entry.updated.text.encode('UTF-8'))
        self.files[f].st_ctime = self._time_convert(entry.published.text.encode('UTF-8'))

    def _time_convert(self, t):
        """
        Purpose: Converts the GData String time to UNIX Time
        t: String representation of GData's time format
        Returns: Integer conversion of t in UNIX Time
        """
        return int(time.mktime(tuple([int(x) for x in (t[:10].split('-')) + t[11:19].split(':')]) + (0,0,0)))

def main():
    """
    Purpose: Mount the filesystem
    Returns: 0 To indicate successful operation
    """

    usage = """Google Docs FS: Mounts Google Docs files on a local
    filesystem gFile.py email password mountpoint""" + fuse.Fuse.fusage

    gfs = GFile(sys.argv[1], sys.argv[2], version = "%prog " + fuse.__version__,
        usage = usage, dash_s_do='setsingle')
    gfs.parse(errex=1)
    gfs.main()

    return 0

if __name__ == '__main__':
    main()
