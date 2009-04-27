#!/usr/bin/env python2.5
#
#   gFile.py
#
#   Copyright 2008-2009 Scott C. Walton <d38dm8nw81k1ng@gmail.com>
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
import platform
import errno
import time
import fuse
import gNet
import getpass

from subprocess import *

fuse.fuse_python_api = (0,2)

class GStat(object):
    """
    The stat class to use for getattr
    """
    def __init__(self):
        """
        Purpose: Sets the attributes to folder attributes
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

    def set_file_attr(self, size):
        """
        Purpose: Set attributes of a file
        size: int the file's size in bytes
        """
        self.st_mode = stat.S_IFREG | 0744
        self.st_nlink = 2
        self.st_size = size

    def set_access_times(self, mtime, ctime, atime = None):
        """
        Purpose: Set the access times of a file
        mtime: int modified time
        ctime: int creation time
        atime: int access time
        """
        self.st_mtime = mtime
        self.st_atime = ctime
        if atime is not None:
            self.st_atime = atime

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

        super(GFile, self).__init__(*args, **kw)
        self.gn = gNet.GNet(em, pw)
        self.directories = {}
        self.files = {}
        self.written = {}
        self.time_accessed = {}
        self.to_upload = {}
        self.special_patterns = ['~lock', 'DS_Store']


    def getattr(self, path):
        """
        Purpose: Get information about a file
        path: String containing relative path to file using mountpoint as /
        Returns: a GStat object with some updated values
        """

        filename = os.path.basename(path)
        self.files[''] = GStat()
        if filename in self.files:
            st = self.files[filename]
        else:
            return -errno.ENOENT
        # Set proper attributes for files and directories
        if path == '/': # Root
            pass
        elif filename in self.directories: # Is a directory
            pass
        elif filename in self.directories[path.split('/')[-2]]: # Is a file
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

        ## Mac OS X Compatibility
        if platform.system() == 'Darwin':
            dirents.extend(('._.', '.DS_Store'))
            
        if path == '/': # Root
            excludes = []
            self.directories[''] = []
            feed = self.gn.get_docs(filetypes = ['folder'])
            print feed
            for dir in feed.entry:
                excludes.append('-' + dir.title.text.encode('UTF-8'))
                self.directories[dir.title.text.encode('UTF-8')] = []
            if len(excludes) > 0:
                feed = self.gn.get_docs(filetypes = excludes)
            else:
                feed = self.gn.get_docs() # All must in root folder
                
            for file in feed.entry:
                if file.GetDocumentType() == 'folder':
                    self.directories[''].append(file.title.text.encode('UTF-8'))
                else:
                    self.directories[''].append('%s.%s' % (file.title.text.encode('UTF-8'), self._file_extension(file)))
            
            print excludes
            
        else: #Directory
            self.directories[pe[-1]] = []
            feed = self.gn.get_docs(folder = pe[-1])
            print feed
            for file in feed.entry:
                if file.GetDocumentType() == 'folder':
                    self.directories[file.title.text.encode('UTF-8')]
                    self.directories[pe[-1]].append(file.title.text.encode('UTF-8'))
                else:
                    self.directories[pe[-1]].append('%s.%s' % (file.title.text.encode('UTF-8'), self._file_extension(file)))
        for entry in self.directories[pe[-1]]:
            dirents.append(entry)
            
        print self.directories
        print dirents
        # Set the appropriate attributes for use with getattr()
        for file in feed.entry:
            self._setattr(file)

        for r in dirents:
            yield fuse.Direntry(r)

    def mknod(self, path, mode, dev):
        """
        Purpose: Create file nodes. Use mkdir to create directories
        path: Path of file to create
        mode: Ignored (for now)
        dev: Ignored (for now)
        Returns: 0 to indicate succes
        """
        ## TODO: Might see if I can get away with not implementing this
        print "----\nMKNOD\n----"
        filename = os.path.basename(path)
        print filename
        self.to_upload[path] = True
        print self.to_upload
        self.files[filename] = GStat()
        print self.files
        self.files[filename].set_file_attr(0)
        self.directories[path.split('/')[-2]].append(filename)
        print self.directories
        return 0

    def open(self, path, flags):
        """
        Purpose: Open the file referred to by path
        path: String giving the path to the file to open
        flags: String giving Read/Write/Append Flags to apply to file
        Returns: Pointer to file
        """

        ## I think that's all of them. The others are just different
        ## ways of representing the one defined here
        ## TODO: Rewrite this so the file isn't downloaded on write
        ## Buffer will just be written to a new temporary file and this
        ## will then be uploaded
        if flags == 32768:
            f = 'r'
        elif flags == 32769:
            f = 'w'
        elif flags == 32770:
            f = 'r+'
        elif flags == 33793:
            f = 'a'
        elif flags == 33794:
            f = 'a+'
        else: # Assume that it was passed from self.read()
            f = flags
        print "Flag is: ", f
        if f != 'w': # Download only when you want to read the file
            if not os.path.exists('/tmp/google-docs-fs/' + os.path.basename(path)):
                file = self.gn.get_file(path, f)
            else:
                file = open('/tmp/google-docs-fs/' + os.path.basename(path), f)
        else:
            print os.path.basename(path)
            file = open('/tmp/google-docs-fs/' + os.path.basename(path), f)
                            
        print self.files
        print file
        self.files[os.path.basename(path)].st_size = os.path.getsize('/tmp/google-docs-fs/' + os.path.basename(path))
        return file

    def write(self, path, buf, offset, fh = None):
        """
        Purpose: Write the file to Google Docs
        path: Path of the file to write as String
        buf: Data to write to Google Docs
        offset: Ignored (for now)
        fh: File to read
        Returns: 0 to indicate success
        """

        print "------\nWRITE\n------"
        tmp_path = ('/tmp/google-docs-fs/' + os.path.basename(path))
        if fh is None:
            fh = open(tmp_path, 'wb')
        fh.seek(offset)
        print "-- OFFSET ", offset, " --"
        print "BUFFER:", len(buf)
        fh.write(buf)
        self.written[tmp_path] = True
        self.time_accessed[tmp_path] = time.time()
        self.time_accessed[tmp_path] = time.time()
        print self.time_accessed
        return len(buf)
        ##TODO: Fix Me

    def flush(self, path, fh = None):
        """
        Purpose: Flush the write data and upload it to Google Docs
        path: String containing path to file to flush
        fh: File Handle
        """
        print "---\nFlush\n---"
        print fh
        if fh is not None:
            fh.close()

    def unlink(self, path):
        """
        Purpose: Remove a file
        path: String containing relative path to file using mountpoint as /
        """
        filename = os.path.basename(path)
        if filename in self.directories:
            for d in self.directories:
                if filename in d and path.split('/')[-2] == d:
                    self.gn.erase(path)
            return -errno.EISDIR
        try:
            self.gn.erase(path)
        except AttributeError, e:
            return -errno.ENOENT
        # TODO: Finish Me! ?

    def read(self, path, size = -1, offset = 0, fh = None):
        """
        Purpose: Read from file pointed to by fh
        path: String Path to file if fh is None
        size: Int Number of bytes to read
        offset: Int Offset to start reading from
        fh: File to read
        Returns: Bytes read
        """

        ## TODO: Make me work with spreadsheets
        if fh is None:
            fh = self.open(path, 'rb+')

        print offset
        fh.seek(offset)
        buf = fh.read(size)
        tmp_path = '/tmp/google-docs-fs/' + os.path.basename(path)
        self.time_accessed[tmp_path] = time.time()
        return buf

    def release(self, path, flags, fh = None):
        """
        Purpose: Called after a file is closed
        path: String containing path to file to be released
        flags: Ignored
        fh: File Handle to be released
        """

        print '------\nRELEASE\n------'
        tmp_path = '/tmp/google-docs-fs/' + os.path.basename(path)

        if path in self.to_upload and tmp_path in self.written:
            self.gn.upload_file(path)
            del self.to_upload[path]
        
        if os.path.exists(tmp_path):
            if tmp_path in self.written:
                self.gn.update_file_contents(path)
                del self.written[tmp_path]
                        
        print self.time_accessed    
        for t in self.time_accessed:
            print t
            if time.time() - self.time_accessed[t] > 300:
                os.remove(t)

    def mkdir(self, path, mode):
        """
        Purpose: Make a directory
        path: String containing path to directory to create
        mode: Ignored (for now)
        """
        print "mkdir"
        print path.split('/')
        name = os.path.basename(path)
        if name in self.directories:
            if name in self.directories[path.split('/')[-2]]:
                return -errno.EEXIST
        try:
            self.directories[path.split('/')[-2]].append(name)
        except KeyError:
            return -errno.ENOENT

        self.gn.make_folder(path)
        self.directories[name] = []
        self._setattr(self.gn.get_filename(path, showfolders = 'true'))
        print self.directories
        print self.files
        
        return 0

    def rmdir(self, path):
        """
        Purpose: Remove a directory referenced by path
        path: String containing path to directory to remove
        """
        filename = os.path.basename(path)
        self.readdir(path, 0)
        print self.directories
        if filename in self.directories:
            if len(self.directories[filename]) == 0:
                for d in self.directories:
                    if d == path.split('/')[-2] and filename in self.directories[d]:
                        self.gn.erase(path, folder = True)
                        deldir = True
                        self.directories[path.split('/')[-2]].remove(filename)
                if deldir:
                    del self.directories[filename]
            else:
                return -errno.ENOTEMPTY
        else:
            return -errno.ENOENT
        return 0

    def rename(self, pathfrom, pathto):
        """
        Purpose: Move file to new location. Cannot rename in place.
        pathfrom: String path of file to move
        pathto: String new file path
        """
        print "rename"
        
        pef = pathfrom.split('/')
        pet = pathto.split('/')
        
        if len(pef) == len(pet):
            for f, t in pef, pet:
                if f != t:
                    self.gn.move_file(pathfrom, pathto)
                    break
            else:
                return -errno.ESAMEDIR
        else:
            self.gn.move_file(pathfrom, pathto)
            
        return 0

    def _setattr(self, entry):
        """
        Purpose: Set the getattr information for entry
        entry: DocumentListEntry object to extract data from
        """
        f = entry.title.text.encode('UTF-8')

        if entry.GetDocumentType() == 'folder':
            self.files[f] = GStat()

        else: #File
            f = '%s.%s' % (f, self._file_extension(entry))
            self.files[f] = GStat()
            self.files[f].set_file_attr(len(f)) # TODO: try and change len(f) to the actual size

        #Set times
        if entry.lastViewed is None:
            self.files[f].set_access_times(self._time_convert(entry.updated.text.encode('UTF-8')),
                                       self._time_convert(entry.published.text.encode('UTF-8')))

        else:
            self.files[f].set_access_times(self._time_convert(entry.updated.text.encode('UTF-8')),
                                       self._time_convert(entry.published.text.encode('UTF-8')),
                                       self._time_convert(entry.lastViewed.text.encode('UTF-8')))

        # Get File sizes
        if os.path.exists('/tmp/google-docs-fs/' + f):
            self.files[f].st_size = os.path.getsize('/tmp/google-docs-fs/' + f)




    def _time_convert(self, t):
        """
        Purpose: Converts the GData String time to UNIX Time
        t: String representation of GData's time format
        Returns: Integer conversion of t in UNIX Time
        """
        return int(time.mktime(tuple([int(x) for x in (t[:10].split('-')) + t[11:19].split(':')]) + (0,0,0)))

    def _file_extension(self, entry):
        """
        Purpose: Determine the file extension for the given entry
        entry: DocumentListEntry object to scan for filetype
        Returns: String of length 3 with file extension (Currently only Oasis filetypes)
        """

        if entry.GetDocumentType() == 'document':
            return 'doc'
        elif entry.GetDocumentType() == 'spreadsheet':
            return 'xls'
        elif entry.GetDocumentType() == 'presentation':
            return 'ppt'

        #Should never reach this - used for debugging
        return entry.GetDocumentType()

def main():
    """
    Purpose: Mount the filesystem
    Returns: 0 To indicate successful operation
    """

    usage = """Google Docs FS: Mounts Google Docs files on a local
    filesystem gFile.py email password mountpoint""" + fuse.Fuse.fusage

    passwd = None
    while not passwd:
        passwd = getpass.getpass()
        
    gfs = GFile(sys.argv[1], passwd, version = "%prog " + fuse.__version__,
        usage = usage, dash_s_do='setsingle')
    gfs.parse(errex=1)
    gfs.main()

    return 0

if __name__ == '__main__':
    main()
