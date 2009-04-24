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
