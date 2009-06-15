#!/usr/bin/env python2.5
#
#   gNet.py
#
#   Copyright 2009 Scott C. Walton <d38dm8nw81k1ng@gmail.com>
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

import os
import gdata.docs.service
import gdata.docs
from gdata import MediaSource

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
            query.AddNamedFolder(self.gd_client.email, folder.encode('utf-8'))

        return self.gd_client.Query(query.ToUri())

    def get_filename(self, path, showfolders = 'false'):
        """
        Purpose: Retrieves the file referred to by path from Google
        path: A String containing the path elements of the file
        showfolders: Either 'true' or 'false' - whether get_filename
                     should also retrieve folders (default: 'false')
        Returns: The gdata List Entry object containing the file or -1 if none exists
        """
        print path
        name = os.path.basename(path)
        title = name.split('.')[0]
        print repr(title)
        pe = path.split('/')
        query = gdata.docs.service.DocumentQuery()
        query['title'] = title.encode('utf-8')
        query['title-exact'] = 'true'
        query['showfolders'] = showfolders

        print "Query works!"
        feed = self.gd_client.Query(query.ToUri())
        filter = []
        # Filter out any files that don't match the case
        for f in feed.entry:
            if f.title.text.decode('utf-8') == title:
                filter.append(f)
        print "Getting filter works!"
        print filter
        # Return the first file encountered in the folder
        # Fix this to be more precise in the final version
        # Need to implement file extensions, then I should be able to
        # check those to get the filetype and a more accurate file
        # May also need to go through the entire file hierarchy to
        # ensure the integrity of the path. May be slower but will be
        # essential to ensure the user doesnt unwittingly erase a
        # random file stored elsewhere
        if len(filter) == 1: ## Assume it is the correct one
            return filter[0]
        for entry in filter:
            print entry.category
            ## Assume that if there's only 1 then it's the correct one.
            if os.path.dirname(path) == '/' or len(entry.category) is 1:
                return entry
            ## This doesn't seem to work any more
            for c in entry.category:
                print c.label
                print pe[-2]
                if pe[-2].encode('utf-8') in c.label:
                    return entry
        
    def erase(self, path, folder = False):
        """
        Purpose: Erase a file
        path: String containing path to the file to erase
        """
        if folder is True:
            file = self.get_filename(path, showfolders = 'true')
        else:
            file = self.get_filename(path)
        self.gd_client.Delete(file.GetEditLink().href)
        ## TODO: Check file exists on server
        ## TODO: Test Me!

    def upload_file(self, path):
        """
        Purpose: Uploads a file to Google Docs
        path: String containing path of the file to be uploaded
        """

        if path.split('/')[-2] != ' ':
            folder = path.split('/')[-2]
        else:
            folder = None

        filename, title, type, mime = self._get_info(path)
        
        print path
        print folder
        print filename
        print title
        print type
        print mime

        media = MediaSource(file_path = '%s%s' % (self.home.encode('utf-8'), filename.encode('utf-8')), content_type = mime)

        if type in ['CSV', 'ODS', 'XLS']:
            self.gd_client.UploadSpreadsheet(media, title)
        if type in ['PPT', 'PPS']:
            self.gd_client.UploadPresentation(media, title)
        else:
            self.gd_client.UploadDocument(media, title)

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

    def get_file(self, path, tmp_path, flags):
        """
        Purpose: Get the file referred to by path off Google Docs.
        path: A string containing the path to the file to download
        flags: A string giving the flags to open the file with
        Returns: The file requested, or -1 if the file doesn't exist
        """

        filename = os.path.basename(path)
        file = self.get_filename(path)
        
        ## Must be a new file
        if file is None:
            import stat
            print "New file"
            os.mknod(tmp_path.encode('utf-8'), 0700 | stat.S_IFREG)
            return open(tmp_path.encode('utf-8'), flags)

        print "\n---------\nFILENAME IS: ", file
        print "---------"
        filetype = file.GetDocumentType()
        if filetype == 'spreadsheet':
            print "Downloading Spreadsheet"
            ## TODO: Make this work - Taken from GData List API Documentation
            import gdata.spreadsheet.service

            spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
            spreadsheets_client.ClientLogin(self.gd_client.email, self.gd_client.password)
            # substitute the spreadsheets token into our gd_client
            docs_auth_token = self.gd_client.GetClientLoginToken()
            self.gd_client.SetClientLoginToken(spreadsheets_client.GetClientLoginToken())
            self.gd_client.DownloadSpreadsheet(file.resourceId.text, tmp_path.encode('utf-8'))
            self.gd_client.SetClientLoginToken(docs_auth_token)

        if filetype == 'presentation':
            print "Downloading Presentation"
            self.gd_client.DownloadPresentation(file.resourceId.text, tmp_path.encode('utf-8'))
        if filetype == 'document':
            print "Downloading Document"
            print file.resourceId.text
            print repr(tmp_path)
            self.gd_client.DownloadDocument(file.resourceId.text, tmp_path.encode('utf-8'))

        return open(tmp_path.encode('utf-8'), flags)

    def update_file_contents(self, path):
        """
        Purpose: Update the contents of the file specified by path
        path: String containing path to file to update
        """
        filename, title, type, mime = self._get_info(path)
        print "Filename:", filename
        print "Title:", title
        print "Type:", type
        print "MIME:", mime
        tmp_path = '%s%s' % (self.home, filename)
        ms = gdata.MediaSource(file_path = tmp_path.encode('utf-8'), content_type = mime)
        entry = self.get_filename(path)
        entry.title.text = title.encode('utf-8')
        self.gd_client.Put(data = entry, uri = entry.GetEditMediaLink().href, media_source = ms)

    def make_folder(self, path):
        """
        Purpose: Create a folder specified by path
        path: String containing path to folder to create
        """
        if os.path.dirname(path) == '/':
            print 1
            self.gd_client.CreateFolder(os.path.basename(path).encode('utf-8'))
        else:
            print 2
            parent_dir = self.get_filename(os.path.dirname(path), showfolders = 'true')
            self.gd_client.CreateFolder(os.path.basename(path).encode('utf-8'), parent_dir)
            
    def move_file(self, pathfrom, pathto):
        """
        Purpose: Move a file from one folder to another
        pathfrom: String containing path to file to move
        pathto: String containing path to move to
        """
        folderfrom = os.path.dirname(pathfrom)
        folderto = os.path.dirname(pathto)
        namefrom = os.path.basename(pathfrom)

        print pathfrom, ">", pathto
        if folderfrom != '/':
            ffe = self.get_filename(folderfrom, showfolders = 'true')
            feed = self.gd_client.GetDocumentListFeed(ffe.content.src)
            for entry in feed.entry:
                if unicode(entry.title.text, 'utf-8') == namefrom[:-4]:
                    entry_from = entry
            self.gd_client.MoveOutOfFolder(entry_from)
        
        entry_from = self.get_filename(pathfrom, showfolders = 'true')
            
        entry_to = self.get_filename(folderto, showfolders = 'true')
        type = entry_from.GetDocumentType()
        if type == 'folder':
            self.gd_client.MoveFolderIntoFolder(entry_from, entry_to)
        elif type == 'document':
            self.gd_client.MoveDocumentIntoFolder(entry_from, entry_to)
        elif type == 'spreadsheet':
            self.gd_client.MoveSpreadsheetIntoFolder(entry_from, entry_to)
        elif type == 'presentation':
            self.gd_client.MovePresentationIntoFolder(entry_from, entry_to)
        
        if os.path.basename(pathfrom) != os.path.basename(pathto):
            entry_from = self.rename_file(entry_from, os.path.basename(pathto))
        
        return 0
    
    def rename_file(self, entry, name_to):
        """
        Purpose: Renames an entry
        entry_from: GDataListEntry to change the name of
        name_to: String name to change to
        Returns: GDataListEntry of renamed file
        """
        entry.title.text = name_to
        return self.gd_client.Put(entry, entry.GetEditLink().href)        
        
    def _get_info(self, path):
        """
        Purpose: Extracts the key parts of a file's name
        path: String containing path to a file to get information about
        Returns: Tuple containing (file_name, file_title, file_type.upper(), mime_type)
        """
        file_name = os.path.basename(path)
        file_title = file_name[:-4]
        file_type = file_name[-3:].upper()
        mime_type = gdata.docs.service.SUPPORTED_FILETYPES[file_type]
        return (file_name, file_title, file_type, mime_type)

def main():
    """
    Purpose: Used for Testing Only.
    Returns: 0 to indicate successful execution
    """
    return 0

if __name__ == '__main__':
    main()
