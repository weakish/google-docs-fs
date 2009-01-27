#!/usr/bin/env python
#
#   gNet.py
#       
#   Copyright 2009 Scott C. Walton <d38dm8nw81k1ng@gmail.com>
#       
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License (version 2), as
#   oublished by the Free Software Foundation
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

import gdata.docs.service
import gdata.docs




class GNet(object):
    """
    Performs all the main interfacing with Google Docs server as well
    as storing the user's session data
    """
    def __init__(self, em, pw):
        """
        Purpose: Login to Google Docs and store the session cookie
        em: The user's email address
        pw: The user's password
        Returns: A GNet object for accessing the GData Docs
        """
        self.gd_client = gdata.docs.service.DocsService()
        self.gd_client.email = em
        self.gd_client.password = pw
        self.gd_client.source = 'google-docs-fs' # Perhaps set a number after this?
        self.gd_client.ProgrammaticLogin()
    
    def get_docs(self):
        """
        Purpose: Retrieve a list of all documents
        Returns: A list of all the user's documents
        """
        return self.gd_client.GetDocumentListFeed()

def main():
    """
    Purpose: Used for Testing Only
    Returns: 0 to indicate successful execution
    """
    from sys import argv
    
    gn_test = GNet(argv[1], argv[2])
    
    #The following doesn't actually work the way I want it
    #It's supposed to print out a list of ALL documents on the server
    #but for some reason it only lists one. Need to test on other machines/
    #accounts, see if I can work it out. Seems to work in gFile.py anyway...
    feed = gn_test.get_docs()

    for i, entry in enumerate(feed.entry):
        print i, entry.title.text.encode('UTF-8')
    
	return 0

if __name__ == '__main__':
    main()
