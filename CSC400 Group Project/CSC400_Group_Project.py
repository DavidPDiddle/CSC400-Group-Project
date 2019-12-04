"""
Group: David Doyle, Skye LeForge, Logan Barker
Class: CSC400
Date: 12/3/2019
Purpose: Read an Ext2 file system using only read-sector calls. It should be able to:
    - Open the file system and set current directory to the root directory
    - Change the current directory to a subdirectory of the current directory
    - Change the current directory to the parent of the current directory
    - Display names and sizes of all files in the directory
    - Copy the contents of a file and save it
"""

# the class keeps track of the block we are currently in
class Ext2Traverser:
    def __init__(self, file_path):
        # load the entire file system in from the file
        self.file_system = open(file_path, mode='rb').read()
        # initialize the rest of the necessary information
        # this will be modified with the first load_fs pass
        self.current_block_group = 0
        self.block_size = 0
        self.blocks_per_group = 0
        self.superblock = []
        self.block_group_desc_table = []
        self.inode_table = 0
        self.inodes_per_group = 0
        self.root_inode = []
        self.current_inode = []
        
    # loads the file into a class object and initializes all of the needed variables
    # starts in block group 0
    def load_fs(self):
        # load in the entire filesystem
        # define the superblock for the block group
        self.superblock = self.file_system[1024:2048]
        # get the block group description table
        self.block_group_desc_table = self.file_system[2048:3072]
        # calculate block size for this filesystem
        self.block_size = 1024 << self.to_int(self.superblock[24:28])
        # get the number of blocks per group
        self.blocks_per_group = self.to_int(self.superblock[32:36])
        # get the inode table location for block 0
        self.inode_table = self.to_int(self.block_group_desc_table[8:12])
        # get the root directory inode
        self.root_inode = self.file_system[1024*inode_table+(128*1):1024*(inode_table)+(128*2)]
        # the number of inodes per group
        self.inodes_per_group = self.superblock[40:44]

    # copies the contents of a file in the ext2 system and save it to a file on your local machine
    def copy_data_to_file(self):
        # get the amount of blocks that the data in the file spans
        blocks_count = (self.to_int(first_data_inode[28:32]))//2
        # initialize a result string that will hold the decoded contents
        result = ""
        for i in range(min(12, blocks_count)):
            # get the block number of the next data location
            block_number = self.to_int(first_data_inode[40+(4*i):44+(4*i)])
            # add decoded data to the result string
            result += file_system[1024*(block_number):1024*(block_number+1)].decode('utf-8')

        # if the number of blocks is greater than 12, go to the indirect blocks
        if blocks_count > 12:
            # get the block number holding the indirect data
            block_number = self.to_int(first_data_inode[40+(4*12):44+(4*12)])
            # load the block into a variable
            indirect_blocks = file_system[1024*block_number:1024*(block_number+1)]

            for i in range(blocks_count-13):
                block_number = self.to_int(indirect_blocks[4*i:4*(i+1)])
                result += file_system[1024*(block_number):1024*(block_number)+1024].decode('utf-8')

        # create a new file to hold the result
        result_file = open("output.txt", "w")
        # write the result to the file
        result_file.write(result)

    # lists the subdirectories and files in the present location
    def list_subdirectories(self):
        # self.current_block
        # keeps track of the position in the block
        position = 0
        # signals if the length to the next entry is 0
        rec_len_zero = False
        while not rec_len_zero:
            # get the amount of bytes until the next record
            record_length = self.to_int(data[position+4:position+6])
            # if it's 0, we have reached the end of the directory and can stop
            if record_length == 0:
                rec_len_zero = True
            # other wise, read and list the names of the files or subdirectories
            else:
                # length of the name of the file or directory
                name_length = self.to_int(data[position+6:position+7])
                # get the file type of this entry
                # 1 - regular file, 2 - directory
                file_type = self.to_int(data[position+7:position+8])
                # get the name of the entry
                name = str(data[position+8:position+8+name_length].decode('utf-8'))
                # print the name to the console
                print(name)
                # go to the beginning of the next entry
                position += record_length

    # go to a new directory location
    def change_directory(self):
        # get block number of the directory
        # set a class value to that new block value
        # set up an array to carry each item and its inode
        # check user input against the name string
        # if it matches and its number is 2, go to it
        # if not, display an error message
        return 0

    # method to handle converting bit arrays to integers
    def to_int(self, bitarray):
        return int.from_bytes(bitarray, byteorder='little')

    # method to calculate which block group the inode is in
    def inode_block_group_location(self, inode_index):
        return (inode_index - 1)/self.inodes_per_group

    # method to calculate the local index of the inode in its block
    def local_inode_index(self, inode_index):
        return (inode_index - 1) % self.inodes_per_group


# testing methods down here before putting them in the class

file_system = open("C:/Users/15022/Documents/CSC400/virtdisk", mode='rb').read()

superblock = file_system[1024:2048]
first_inode = superblock[40:44]

block_group_desc_table = file_system[2048:3072]
inode_table = block_group_desc_table[8:12]
inode_table = int.from_bytes(inode_table, byteorder='little')
print("Inode table:", inode_table)

# find the root inode
root_inode = file_system[1024*inode_table+(128*1):1024*(inode_table)+(128*2)]

# get the number of blocks in the root inode
blocks_count = (int.from_bytes(root_inode[28:32], byteorder='little'))//2
print("Blocks count:",blocks_count)

block_number = int.from_bytes(root_inode[40:44], byteorder='little')
data = file_system[1024*(block_number):1024*(block_number+1)]
a = 0
sub_directory_array = []
rec_len_zero = False
while not rec_len_zero:
    record_length = int.from_bytes(data[a+4:a+6], byteorder='little')
    if record_length == 0:
        rec_len_zero = True
    else:
        name_length = int.from_bytes(data[a+6:a+7], byteorder='little')
        directory_type = int.from_bytes(data[a+7:a+8], byteorder='little')
        inode_location = int.from_bytes(data[a:a+4], byteorder='little')
        name = str(data[a+8:a+8+name_length].decode('utf-8'))
        print(directory_type, name)
        sub_directory_array.append([inode_location, name])
        a += record_length

print(sub_directory_array)
# 3841 inode is for a directory
inode_11 = file_system[1024*(8192+inode_table)+(128*0):1024*(8192+inode_table)+(128*1)]
# get the block count
blocks_count = (int.from_bytes(inode_11[28:32], byteorder='little'))//2
print("Blocks count:",blocks_count)
inodes_per_group = int.from_bytes(superblock[40:44], byteorder='little')
# 1920
print("Inodes per group:", inodes_per_group)
# find the block number the data is stored in
block_number = int.from_bytes(inode_11[40:44], byteorder='little')
data = file_system[1024*(block_number):1024*(block_number+1)]
a = 0
sub_directory_array = []
rec_len_zero = False
while not rec_len_zero:
    record_length = int.from_bytes(data[a+4:a+6], byteorder='little')
    if record_length == 0:
        rec_len_zero = True
    else:
        name_length = int.from_bytes(data[a+6:a+7], byteorder='little')
        directory_type = int.from_bytes(data[a+7:a+8], byteorder='little')
        inode_location = int.from_bytes(data[a:a+4], byteorder='little')
        name = str(data[a+8:a+8+name_length].decode('utf-8'))
        print(directory_type, name)
        sub_directory_array.append([inode_location, name])
        a += record_length

# start in root directory
# have user be able to ls and see the subdirectories
# have user be able to cd into any directory
# able to copy file contents to some output

# the main method will handle all of the user actions
# if __name__ == '__main__':