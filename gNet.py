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

    def get_filename(self, path, showfolders = 'false'):
        """
        Purpose: Retrieves the file referred to by path from Google
        path: A list containing the path elements of the file
        showfolders: Either 'true' or 'false' - whether get_filename
                     should also retrieve folders (default: 'false')
        Returns: The gdata List Entry object containing the file or -1 if none exists
        """
        query = gdata.docs.service.DocumentQuery()
        query['title'] = path[-1]
        query['title-exact'] = 'true'
        query['showfolders'] = showfolders

        feed = self.gd_client.Query(query.ToUri())
        filter = []
        # Filter out any files that don't match the case
        for f in feed.entry:
            if f.title.text.encode('UTF-8') == path[-1]:
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
            if path[-2] is '' and len(entry.category) is 1:
                return entry
            for c in entry.category:
                if path[-2] in c.label:
                    return entry
            #elif path[-2] in (entry.category[0].label, entry.category[1].label):
            #    return entry
        raise IOError, 'File not on Google Docs'

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

        file_len = 0

        for line in file.readlines():
            for word in line:
                for char in word:
                    file_len += 1

        if len(filename) > 1:
            folder = filename[-2]
        else:
            folder = None

        file_title = filename[-1][:-4]
        print filename
        print folder
        filetype = filename[-1][-3:].upper()
        print filetype
        print file_title

        #Set the MIME type for use with MediaSource
        if filetype not in gdata.docs.service.SUPPORTED_FILETYPES:
            raise IOError
        else:
            mime_type = gdata.docs.service.SUPPORTED_FILETYPES[filetype]

        media = MediaSource(file_handle = file, content_type = mime_type, content_length = file_len, file_name = filename[-1])

        if filetype in ['CSV', 'ODS', 'XLS']:
            self.gd_client.UploadSpreadsheet(media, file_title)
        if filetype in ['PPT', 'PPS']:
            self.gd_client.UploadPresentation(media, file_title)
        else:
            self.gd_client.UploadDocument(media, file_title)

    def create_dir(self, path):
        """
        Purpose: Create a directory referred to by path
        path: A list containing the path to the directory to be created
        """

        #Check if folder is in root
        if len(path) > 1:
            parent_dir = path[-2]
        else:
            parent_dir = None

        if parent_dir is None:
            self.gd_client.CreateFolder(path[-1])
        else:
            parent_entry = self.get_filename(parent_dir, showfolders = 'true')
            self.gd_client.CreateFolder(path[-1], parent_entry)

    def get_file(self, path, flags):
        """
        Purpose: Get the file referred to by file off Google Docs.
        path: A string containing the path to the file to download
        flags: A string giving the flags to open the file with
        Returns: The file requested, or -1 if the file doesn't exist
        """
        import os

        # Create the temporary files folder if necessary
        if not os.path.isdir('/tmp/google-docs-fs'):
            os.mkdir('/tmp/google-docs-fs')
        file_path = "%s%s" % ('/tmp/google-docs-fs', path)

        file = self.get_filename(path[:-4].split('/'))
        print "\n---------\nFILENAME IS: ", file
        print "---------"
        filetype = path[-3:].upper()
        if filetype in ['CSV', 'ODS', 'XLS']:
            print "Downloading Spreadsheet"
            ## TODO: Make this work - Taken from GData List API FAQ
            import gdata.spreadsheet.service

            spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
            spreadsheets_client.ClientLogin(self.gd_client.email, self.gd_client.password)
            # substitute the spreadsheets token into our gd_client
            docs_auth_token = self.gd_client.GetClientLoginToken()
            self.gd_client.SetClientLoginToken(spreadsheets_client.GetClientLoginToken())
            self.gd_client.DownloadSpreadsheet(file, file_path)
            self.gd_client.SetClientLoginToken(docs_auth_token)

        if filetype in ['PPT', 'PPS']:
            print "Downloading Presentation"
            self.gd_client.DownloadPresentation(file, file_path)
        else:
            print "Downloading Document"
            self.gd_client.DownloadDocument(file, file_path)

        return open(file_path, flags)


def main():
    """
    Purpose: Used for Testing Only.
    Returns: 0 to indicate successful execution
    """
    return 0

if __name__ == '__main__':
    main()
