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
    
    def get_docs(self, filetypes):
        """
        Purpose: Retrieve a list of all documents
        Returns: A list of all the user's documents
        """
        query = gdata.docs.service.DocumentQuery(categories=filetypes)
        return self.gd_client.Query(query.ToUri())

def main():
    """
    Purpose: Used for Testing Only. Alter it however you want.
    Returns: 0 to indicate successful execution
    """
    
    return 0

if __name__ == '__main__':
    main()
