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

Optionally, append your version of Python to the end of the command:
sudo ./INSTALL.py 2.6
The default is to attempt to install to Python 2.5.

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
2. Trying mkdir in anything other than the root directory doesn't
work.
3. Python 2.6 behaves strangely with gdata-python-client. If you
want to use Python 2.6 then copy the files into the right place
with the following command:
sudo mv /usr/local/lib/python2.6/dist-packages/{atom,gdata*} /usr/lib/python2.6/dist-packages/
