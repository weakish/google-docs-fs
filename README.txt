README
Scott C. Walton
http://code.google.com/p/google-docs-fs

-------------------
SYSTEM REQUIREMENTS
-------------------

Python 2.5
gdata-python-client-1.3.0
python-fuse-0.2
Links to these can be found in the OnlineManual in the Wiki.

-----
LINUX
-----
To install on Linux, simply run the INSTALL.py script as root/sudo:

su -
<password>
./INSTALL.py

or

sudo ./INSTALL.py

At this point in time, I am only supporting Python 2.5 due to strange
errors occuring with Python 2.6 with the Ubuntu 9.04 Beta. I will check
to see if this problem has been solved soon and will update my support
accordingly.

--------
MAC OS X
--------
The INSTALL.py script was not written for Mac OS X and, as such, I can't
guarantee that it will work. You may also need to change the mkdir line
in gmount to another temporary directory (it may work, I don't know OS X
file system layout).
More pressingly, this file system does not work on Mac OS X at this
moment in time. See Issue 3 at:
http://code.google.com/p/google-docs-fs/issues/detail?id=3
I will begin to rectify this on Monday 27th April, when I borrow a
friend's Mac. Until then, sit tight and rest assured that I am going to
fix this.

----------
KNOWN BUGS
----------

1. For reasons I cannot fathom, presentations cannot be uploaded. If
anyone finds that it works for them, can you please let me know?
2. Moving files into the root directory of the file system is also
broken. This is due to errors happening within gdata and I cannot see
any problems with my code. I will be posting on Google Groups to see
if I can get to the bottom of this.
3. Trying mkdir in anything other than the root directory doesn't
work. I have looked at the debug output and it seems to be problems
with gdata-python. I will look into it some more but until then, this
feature is essentially unsupported.


On the bright side, I have actually implemented much more than I expected
to by this time. Making directories and renaming files were not in my
original timescale and so I regard their (partial) inclusion as a bonus.
I'll get to the bottom of these issues and hopefully, I will have a fully
functional file system sooner rather than later.

