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
        em: A String containing the user's email address
        pw: A String containing the user's password
        Returns: A GNet object for accessing the GData Docs
        """
        
        self.gd_client = gdata.docs.service.DocsService()
        self.gd_client.email = em
        self.gd_client.password = pw
        self.gd_client.source = 'google-docs-fs'
        self.gd_client.ProgrammaticLogin()
        
    def get_docs(self, filetypes = None, folder = None):
        """
        Purpose: Retrieve a list of all documents
        filetypes: A List containing the filetypes to query
        folder: A String containing the folder to search in
        Returns: A List of documents specified by filetypes: Type gdata.docs.DocumentListFeed
        """
        
        query = gdata.docs.service.DocumentQuery(categories = filetypes)
        query['showfolders'] = 'true'
        
        if folder is not None:
            query['folder'] = folder

        return self.gd_client.Query(query.ToUri())
        

def main():
    """
    Purpose: Used for Testing Only. Alter it however you want.
    Returns: 0 to indicate successful execution
    """
    
    from sys import argv
    gd_client = gdata.docs.service.DocsService()
    gd_client.email = argv[1]
    gd_client.password = argv[2]
    gd_client.source = 'google-docs-fs'
    gd_client.ProgrammaticLogin()
    
    q = gdata.docs.service.DocumentQuery(categories = None)
    q['showfolders'] = 'true'
    q['category'] = 'folder'
    #q['category'] = '-test'
    
    feed = gd_client.Query(q.ToUri())

    print '\n'
    if(len(feed.entry) == 0):
        print "No entries in feed.\n"
    else:
        #for i in feed.entry:
        #    print i, "\n"
        for i, entry in enumerate(feed.entry):
            print '%s %s %s\n' % (i+1, entry.title.text.encode('UTF-8'), entry.category[0].label)
        
    return 0 

if __name__ == '__main__':
    main()
