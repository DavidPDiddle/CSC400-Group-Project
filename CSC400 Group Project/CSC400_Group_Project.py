"""
Group: David Doyle, Skye LeForge, Ronald Logan Barker, Chance Whittaker
Class: CSC400
Date: 12/3/2019
Purpose: Read an Ext2 file system using only read-sector calls. It should be able to:
    - Open the file system and set current directory to the root directory
    - Change the current directory to a subdirectory of the current directory
    - Change the current directory to the parent of the current directory
    - Display names and sizes of all files in the directory
    - Copy the contents of a file and save it
"""

import io
from PIL import Image

# the class keeps track of the block we are currently in
class Ext2Traverser:
    def __init__(self, file_path):
        # load the entire file system in from the file
        self.file_system = open(file_path, mode='rb').read()
        # the size of an ext2 inode is 128
        self.inode_size = 128
        """initialize the rest of the necessary information
            this will be modified with the first load_fs pass"""
        # the current block group we are in
        self.current_block_group = 0
        # size of each block in the system - 1024 in this implementation
        self.block_size = 0
        # number of blocks in each block group - 8192 in this implementation
        self.blocks_per_group = 0
        # stores the superblock for the filesystem
        self.superblock = []
        # stores the block group descriptor table for the filesystem
        self.block_group_desc_table = []
        # static value for the number of inodes per group - 1920 in this implementation
        self.inodes_per_group = 0
        # holds the system root inode
        self.root_inode = []
        # an array that stores all of the beginning inode table locations by block
        self.inode_array = []
        # holds an array of subdirectory names and their corresponding inodes
        self.subdirectory_array = []
        # holds the current directory inode we are looking at
        self.current_inode = 0
        # number of block groups in the system
        self.num_block_groups = 0
        
    # loads the file into a class object and initializes all of the needed variables
    # starts in block group 0
    def load_fs(self):
        # define the superblock for the block group
        self.superblock = self.file_system[1024:2048]
        # get the block group description table
        self.block_group_desc_table = self.file_system[2048:3072]
        # calculate block size for this filesystem
        self.block_size = 1024 << self.to_int(self.superblock[24:28])
        # get the number of blocks per group
        self.blocks_per_group = self.to_int(self.superblock[32:36])
        # get the number of block groups in the system
        self.num_block_groups = (self.to_int(self.superblock[4:8])//self.to_int(self.superblock[32:36])) + 1
        # get the inode table location for each inode group per block group
        for i in range(self.num_block_groups):
            padding = self.to_int(self.block_group_desc_table[18:20])
            self.inode_array.append(self.to_int(self.block_group_desc_table[8+32*i:12+32*i]))
        # get the root directory inode
        self.root_inode = self.file_system[1024*self.inode_array[0]+(128*1):1024*(self.inode_array[0])+(128*2)]
        # the number of inodes per group - should be 1920 for this implementation
        self.inodes_per_group = self.to_int(self.superblock[40:44])
        # set the current inode to the root inode
        self.current_inode = self.inode_array[0]
        # initialize the subdirectory array
        self.load_subdirectory_array()

    # copies the contents of a file in the ext2 system and save it to a file on your local machine
    def copy_data_to_file(self, file_name):
        # first find the file in the subdirectory array
        inode_location = None
        for i in range(len(self.subdirectory_array)):
            # so, if the name matches and it is a file, get the block location
            if file_name == self.subdirectory_array[i][1] and self.subdirectory_array[i][2] == 1:
                inode_location = self.subdirectory_array[i][0]
        if inode_location == None:
            print("%s is not recognized as a valid file name" % file_name)
            return
        # find out which block group the file is in
        block_group_number = inode_location//self.inodes_per_group
        # find the block location of the inode table we need to use
        inode_table_block = self.inode_array[block_group_number]
        # get the relative location of the inode in its block
        relative_inode_value = (inode_location % self.inodes_per_group)-1
        # get the amount of blocks that the data in the file spans
        file_inode = self.file_system[self.block_size*self.inode_array[block_group_number]+128*(relative_inode_value):
                                                     self.block_size*self.inode_array[block_group_number]+128*(relative_inode_value+1)]
        blocks_count = (self.to_int(file_inode[28:32]))//2
        # does something different based on what type of file it is
        # this statement handles jpg images
        if file_name[-4:].lower() == ".jpg" or file_name[-4:].lower() == ".gif" or file_name[-4:].lower() == ".mp3":
            # initialize the result bytearray
            result_file = open(file_name, "wb")
            for i in range(min(12, blocks_count)):
                # get the block number of the next data location
                block_number = self.to_int(file_inode[40+(4*i):44+(4*i)])
                # append the data bytearray to the result
                result = self.file_system[1024*(block_number):1024*(block_number+1)]
                result_file.write(result)

            # if the number of blocks is greater than 12, go to the indirect blocks
            if blocks_count > 12:
                # get the block number holding the indirect data
                block_number = self.to_int(file_inode[40+(4*12):44+(4*12)])
                # load the block into a variable
                indirect_blocks = self.file_system[1024*block_number:1024*(block_number+1)]
                # get the rest of the data
                for i in range(blocks_count-13):
                    block_number = self.to_int(indirect_blocks[4*i:4*(i+1)])
                    result = self.file_system[1024*(block_number):1024*(block_number)+1024]
                    result_file.write(result)
        else:
            # if the file is a text file, initialize a result string that will hold the decoded contents
            result = ""
            for i in range(min(12, blocks_count)):
                # get the block number of the next data location
                block_number = self.to_int(file_inode[40+(4*i):44+(4*i)])
                # add decoded data to the result string
                result += self.file_system[1024*(block_number):1024*(block_number+1)].decode('utf-8')

            # if the number of blocks is greater than 12, go to the indirect blocks
            if blocks_count > 12:
                # get the block number holding the indirect data
                block_number = self.to_int(file_inode[40+(4*12):44+(4*12)])
                # load the block into a variable
                indirect_blocks = self.file_system[1024*block_number:1024*(block_number+1)]
                # get the rest of the data
                for i in range(blocks_count-13):
                    block_number = self.to_int(indirect_blocks[4*i:4*(i+1)])
                    result += self.file_system[1024*(block_number):1024*(block_number)+1024].decode('utf-8')

            # create a new text file to hold the result with the same name as the file
            result_file = open(file_name, "w")
            # write the result to the file
            result_file.write(result)
            print("Data saved to %s" % file_name)

    # loads the subdirectory array for the current directory
    def load_subdirectory_array(self):
        # find out which block group we are in
        block_group_number = self.current_inode//self.inodes_per_group
        # find the block location of the inode table we need to use
        inode_table_block = self.inode_array[block_group_number]
        if block_group_number == 0:
            # if we are in the root inode table, then the directory will be in the second inode
            inode = self.file_system[self.block_size*inode_table_block+self.inode_size:self.block_size*inode_table_block+self.inode_size*2]
        else:
            # if we are not in the root inode, then the directory is in the first entry
            inode = self.file_system[self.block_size*inode_table_block:self.block_size*inode_table_block+self.inode_size]
        # find the block number the data is stored in
        block_number = self.to_int(inode[40:44])
        # go to that data block
        data_block = self.file_system[self.block_size*block_number:self.block_size*(block_number+1)]
        # keeps track of the position in the block
        position = 0
        # array that holds an item name and whether it is a file or directory
        self.subdirectory_array = []
        # signals if the length to the next entry is 0
        rec_len_zero = False
        while not rec_len_zero:
            # get the amount of bytes until the next record
            record_length = self.to_int(data_block[position+4:position+6])
            # if it's 0, we have reached the end of the directory and can stop
            if record_length == 0:
                rec_len_zero = True
            # other wise, read and list the names of the files or subdirectories
            else:
                # length of the name of the file or directory
                name_length = self.to_int(data_block[position+6:position+7])
                # get the file type of this entry
                # 1 - regular file, 2 - directory
                file_type = self.to_int(data_block[position+7:position+8])
                # get the location of the data inode for this entry
                inode_location = self.to_int(data_block[position:position+4])
                # get the name of the entry
                name = str(data_block[position+8:position+8+name_length].decode('utf-8'))
                # go to the beginning of the next entry
                position += record_length
                # append the inode location and file name to the sub directory array
                self.subdirectory_array.append([inode_location, name, file_type])

    # go to a new directory location
    def change_directory(self, directory_name):
        inode_number = None
        # get block number of the directory, but only if it's a directory
        for i in range(len(self.subdirectory_array)):
            if directory_name == self.subdirectory_array[i][1] and self.subdirectory_array[i][2] == 2:
                inode_number = self.subdirectory_array[i][0]
        # report issues to the user and exit the method if they do not provide valid input
        if inode_number == None:
            print("%s not recognized as a valid directory name" % directory_name)
            return
        # set the current block number to the new directory
        self.current_inode = inode_number
        # update the subdirectory array
        self.load_subdirectory_array()

    def list_subdirectories(self):
        # print the names of the subdirectories and files and size in bytes of the files
        for i in range(len(self.subdirectory_array)):
            # if the entry is a file, print the name as well as the size in bytes
            if self.subdirectory_array[i][2] == 1:
                # this convoluted mess grabs the file size as a bytearray
                file_size = self.file_system[self.block_size*self.inode_array[self.subdirectory_array[i][0]//self.inodes_per_group]+
                                                self.inode_size*(self.subdirectory_array[i][0]%self.inodes_per_group):
                                                    self.block_size*self.inode_array[self.subdirectory_array[i][0]//self.inodes_per_group]+
                                                    self.inode_size*((self.subdirectory_array[i][0]%self.inodes_per_group)+1)][4:8]
                # then convert it to an integer
                file_size = self.to_int(file_size)
                print("%s\t%d bytes" % (self.subdirectory_array[i][1], file_size))
            else:
                print(self.subdirectory_array[i][1])

    # method to handle converting bit arrays to integers
    def to_int(self, bitarray):
        return int.from_bytes(bitarray, byteorder='little')



if __name__ == '__main__':
    # initialize the filesystem
    fs = Ext2Traverser("C:/Users/15022/Documents/CSC400/virtdisk")
    fs.load_fs()

    # simulate the command line
    # allows for ls, cd, open, and quit commands
    done = False
    while not done:
        user_input = input("Enter a command: ")
        if user_input[0:3] == "cd " and len(user_input) > 3:
            fs.change_directory(user_input[3:])
        elif user_input == "ls":
            print("Contents of current directory:")
            fs.list_subdirectories()
        elif user_input[0:5] == "open " and len(user_input) > 5:
            fs.copy_data_to_file(user_input[5:])
        elif user_input == "quit":
            done = True
        else:
            print("Please enter a valid input")
            print("ls - list subdirectories and files")
            print("cd {directory} - change directory")
            print("open {file} - open a file and save it locally")
            print("quit - exit")
        print("\n")