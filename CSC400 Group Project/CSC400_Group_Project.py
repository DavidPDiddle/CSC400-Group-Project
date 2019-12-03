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
    def __init__(self):
        self.current_directory = 0
        self.block_size = 0
        self.blocks_per_group = 0
        self.superblock = []
        self.block_group_desc_table = []
        self.file_system
        self.inode_table = 0
        self.inodes_per_group = 0
        self.root_inode = []
        self.current_inode = []
        
    # loads the file into a class object and initializes all of the needed variables
    # starts in block group 0
    def load_fs(self, filepath):
        # load in the entire filesystem
        file = open(filepath, mode='rb')
        self.file_system = file.read()
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
        self.root_inode = []
        # the number of inodes per group
        self.inodes_per_group = self.superblock[40:44]

    # 
    def copy_data_to_file(self):
        blocks_count = (int.from_bytes(first_data_inode[28:32], byteorder='little'))//2
        result = ""
        for i in range(12):
            block_number = int.from_bytes(first_data_inode[40+(4*i):44+(4*i)], byteorder='little')
            print(block_number)
            print(file_system[1024*(block_number):1024*(block_number+1)])
            result += file_system[1024*(block_number):1024*(block_number+1)].decode('utf-8')

        # go to the indirect blocks
        block_number = int.from_bytes(first_data_inode[40+(4*12):44+(4*12)], byteorder='little')
        new_block = file_system[1024*block_number:1024*(block_number+1)]

        for i in range(blocks_count-12):
            block_number = int.from_bytes(new_block[4*i:4*(i+1)], byteorder='little')
            print(block_number)
            print(file_system[1024*(block_number):1024*(block_number)+1024])
            result += file_system[1024*(block_number):1024*(block_number)+1024].decode('utf-8')

        result_file = open("output.txt", "w")
        result_file.write(result)
        print(result)

    def list_subdirectories(self):
        position = 0
        rec_len_zero = False
        while not rec_len_zero:
            # get the amount of bytes until the next record
            record_length = int.from_bytes(data[position+4:position+6], byteorder='little')
            # if it's 0, we have reached the end of the directory and can stop
            if record_length == 0:
                rec_len_zero = True
            else:
                name_length = int.from_bytes(data[position+6:position+7], byteorder='little')
                print("Record length:",record_length)
                print("Name length:", name_length)
                name = str(data[a+8:a+8+name_length].decode('utf-8')) + '\n'
                print(name)
                a += record_length

    # method to handle converting bit arrays to integers
    def to_int(self, bitarray):
        return int.from_bytes(bitarray, byteorder='little')

    def inode_block_group_location(self, inode_index):
        return (inode_index - 1)/self.inodes_per_group

    def local_inode_index(self, inode_index):
        return (inode_index - 1) % self.inodes_per_group

file = open("C:/Users/15022/Documents/CSC400/virtdisk", mode='rb')
file_system = file.read()

superblock = file_system[1024:2048]
first_inode = superblock[40:44]

block_group_desc_table = file_system[2048:3072]
inode_table = block_group_desc_table[8:12]
inode_table = int.from_bytes(inode_table, byteorder='little')

first_data_inode = file_system[1024*inode_table+(128*1):1024*(inode_table)+(128*2)]

#block_number = int.from_bytes(first_data_inode[40+(4*i):44+(4*i)], byteorder='little')

blocks_count = (int.from_bytes(first_data_inode[28:32], byteorder='little'))//2
result = ""
block_number = int.from_bytes(first_data_inode[40:44], byteorder='little')
print("Block number:", block_number)
data = file_system[1024*(block_number):1024*(block_number+1)]
print(data)
a = 0
rec_len_zero = False
while not rec_len_zero:
    record_length = int.from_bytes(data[a+4:a+6], byteorder='little')
    if record_length == 0:
        rec_len_zero = True
    else:
        name_length = int.from_bytes(data[a+6:a+7], byteorder='little')
        print("Record length:",record_length)
        print("Name length:", name_length)
        name = str(data[a+8:a+8+name_length].decode('utf-8')) + '\n'
        print(name)
        a += record_length

# go to the indirect blocks
block_number = int.from_bytes(first_data_inode[40+(4*12):44+(4*12)], byteorder='little')
new_block = file_system[1024*block_number:1024*(block_number+1)]

#for i in range(blocks_count-12):
#    block_number = int.from_bytes(new_block[4*i:4*(i+1)], byteorder='little')
#    print(block_number)
#    print(file_system[1024*(block_number):1024*(block_number)+1024])
#    result += file_system[1024*(block_number):1024*(block_number)+1024].decode('utf-8')

#result_file = open("output.txt", "w")
#result_file.write(result)


# start in root directory
# have user be able to ls and see the subdirectories
# have user be able to cd into any directory
# able to copy file contents to some output