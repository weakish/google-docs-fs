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
from gdata import MediaSource

##########
### NOTE TO SELF:
### UploadDocument
### UploadPresentation
### UploadSpreadsheet
### GetMedia
### ? GetMediaURL ?
### MediaSource Object
##########
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
        
    def get_filename(self, pe, showfolders = 'false'):
        """
        Purpose: Retrieves the file referred to by path from Google
        pe: A list containing the path elements of the file
        showfolders: Either 'true' or 'false' - whether get_filename
                     should also retrieve folders (default: 'false')
        Returns: The gdata List Entry object containing the file or -1 if none exists
        """
        query = gdata.docs.service.DocumentQuery()
        query['title'] = pe[-1]
        query['title-exact'] = 'true'
        query['showfolders'] = showfolders
        
        feed = self.gd_client.Query(query.ToUri())
        filter = []
        # Filter out any files that don't match the case
        for f in feed.entry:
            if f.title.text.encode('UTF-8') == pe[-1]:
                filter.append(f)
                
        # Return the first file encountered in the folder
        # Fix this to be more precise in the final version
        # Need to implement file extensions, then I should be able to
        # check those to get the filetype and a more accurate file
        # May also need to go through the entire file hierarchy to
        # ensure the integrity of the path. May be slower but will be
        # essential to ensure the user doesnt unwittingly erase a
        # random file stored elsewhere
        for entry in filter:
            if pe[-2] is '' and len(entry.category) is 1:
                return entry
            elif pe[-2] in (entry.category[0].label, entry.category[1].label):
                return entry
        return -1
        
    def erase(self, file):
        """
        Purpose: Erase a file
        file: A gdata entry object containing the file to erase
        """
        self.gd_client.Delete(file.GetEditLink().href)
        ## TODO: Check file exists on server
        ## TODO: Test Me!
        
    
    def upload_file(self, filename, file):
        """
        Purpose: Uploads a file to Google Docs
        filename: List containing the path to the file to upload
        file: The actual document to upload
        """
        folder = filename[-2]
        filetype = filename[-1][-3:]
        mime_type = ""
        
        ## TODO: Add support for MS Office file types
        if filetype == 'odt':
            mime_type = 'application/vnd.oasis.opendocument.text'
            upload = self.gd_client.UploadDocument
        elif filetype == 'ods':
            mime_type = 'application/vnd.oasis.opendocument.spreadsheet'
            upload = self.gd_client.UploadSpreadsheet
        elif filetype == 'odp':
            mime_type = 'application/vnd.oasis.opendocument.presentation'
            upload = self.gd_client.UploadPresentation
        
        media = MediaSource(file, mime_type, len(buf), filename[-1])
        upload(media, filename[-1][:-4])
        
    def get_file(self, file):
        """
        Purpose: Get the file referred to by file off Google Docs
        file: A list containing the path to the file to download
        Returns: The file requested, or -1 if the file doesn't exist
        """
        #TODO: Finish Me!
        pass

def main():
    """
    Purpose: Used for Testing Only.
    Returns: 0 to indicate successful execution
    """
    return 0 

if __name__ == '__main__':
    main()
