#!/usr/bin/env python
#
#   gFS.py
#   
#   Copyright 2008 Scott Walton <d38dm8nw81k1ng@gmail.com>
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

import fuse
import stat
import os
import errno

from time import time
from subprocess import *

fuse.fuse_python_api = (0,2)

class GStat(fuse.stat):
	"""
	The stat class to use for getattr
	"""
	def __init__(self):
		self.st_mode = stat.S_IFDIR || 0755
		self.st_ino = 0
		self.st_dev = 0
		self.st_nlink = 2
		self.st_uid = stat.ST_UID
		self.st_gid = stat.ST_GID
		self.st_size = 4096
		self.st_atime = 0
		self.st_mtime = 0
		self.st_ctime = 0
		
		
class GDocFS(fuse.Fuse):
	""" 
	The main Google Docs filesystem class. Most work will be done
	in here.
	"""
	def __init__(self, *args, **kw):
		""" 
		Connect to the Google Docs Server and verify credentials
		"""
		fuse.Fuse.__init__(self, *args, **kw)
	
	def getattr(self, path):
		"""
        - st_mode (protection bits)
        - st_ino (inode number)
        - st_dev (device)
        - st_nlink (number of hard links)
        - st_uid (user ID of owner)
        - st_gid (group ID of owner)
        - st_size (size of file, in bytes)
        - st_atime (time of most recent access)
        - st_mtime (time of most recent content modification)
        - st_ctime (platform dependent; time of most recent metadata change on Unix,
                    or the time of creation on Windows).
        """
        st = GStat()
        pe = path.split('/')[1:]
        st.st_atime = int(time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime
        

	def getdir(self, path):
		"""
        return: [[('file1', 0), ('file2', 0), ... ]]
        """
		pass

	def chmod(self, path, mode):
		pass
	
	def chown(self, path, uid, gid):
		pass
		
	def fsync(self, path, isFsyncFile):
		pass
		
	def link(self, targetPath, linkPath):
		pass
		
	def mkdir(self, path, mode):
		pass
		
	def mknod(self, path, mode, dev):
		pass
		
	def open(self, path, flags):
		pass
		
	def read(self, path, length, offset):
		pass
	
	def readlink(self, path):
		pass
		
	def release(self, path, flags):
		pass
		
	def rename(self, oldPath, newPath):
		pass
		
	def rmdir(self, path):
		pass
		
	def statfs(self):
		pass
		
	def truncate(self, path, size):
		pass
		
	def unlink(self, path):
		pass
		
	def utime(self, path, times):
		pass
		
	def write(self, path, buf, offset):
		pass
	
	

def main():
	
	return 0

if __name__ == '__main__':
	main()
