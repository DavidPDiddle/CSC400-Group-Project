"""
Group: David Doyle, Skye LeForge, Logan Barker
Class: CSC400
Date: 12/3/2019
Purpose: Read an Ext2 file system using only read-sector calls. It should be able to:
    - Open the file system and set current directory to the root directory
    - Change the current directory to a subdirectory of the current directory
    - Change the current directory to the parent of the current directory
    - Display names and sizes of all files in the directory
    - Copy the contents of a file
"""

class Ext2:
    def __init__(self, io, parent=None, root=None):
        self.io = io
        self.parent = parent
        self.root = root

