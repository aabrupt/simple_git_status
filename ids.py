import os
import hashlib
# This is a global string that contain information about the name of the file that where the data is stored.
# Since this is a globally scoped file it is using the camel screaming-snake-case in the name.
FILENAME = ".protection"


# This function will give us the correctly formatted path based on the operating systems specification.
# The function will use the global variable containing the file name of the file that will store information about the protected files.
def protection_file(root_dir):
    """
    This function uses the global FILENAME combined with a root directory to give a path that is correctly formatted based on the operating system specifications.
    params:
    root_dir: string that is a corredtly formatted path

    returns:
    string that is a correctly formatted path
    """
    return os.path.join(root_dir, FILENAME)

# A simple function that walks the filesystem based on the root directory provided.
def find_files(root_path):
    """
    This is a custom implementation of os.walk that uses recursion.

    # Safety:
    You need to ensure that the given path is a folder beacuse this assumes this for preformance resons in the recursion. If it was nonrecursive then it would not have sutch conserns.

    # Errors:
    If a given directory has to many files or folders it could exceed the ram of the program
    beacuse it needs to be an array and not an iterator witch would be better.
    └── directory
        ├── file_1
        ├── file_2
        ├── file_3
        ├── ...
        ├── file_alot

    If there is a folder that is too deeply nested it will fail if the ram for the python process is less than the string for the folder and the other folder strings in the previous recursions. For infinite recursion it would actually be exponential memory use.
    ./really/long/path/..../file
    Theoretically it could crash with a single file if that filename is bigger than the ram availible but that is not a case we should worry about.

    params:
    root_dir: string that is a correctly formatted path

    returns:
    Array of strings that are correctly formatted paths
    """
    # The collection of files that will appended to by this function.
    files = []
    # `os.listdir` takes in a path and returns a list of relative paths based on the root_path that is inputted into the function. This list is then looped through using a for-loop.
    for dir in os.listdir(root_path):
        # We rebase the search onto the new directory that is found using the `os.listdir` function.
        # this path is garanted to exist beacuse we just got all the path in the current directory
        new_path = os.path.join(root_path, dir)
        # We do not hash our own file beacue it would allways be modified beacuse the data would be one step behind
        # If we where to do that then we should provide the content ourselfs so it would be sort of like a checksum
        # not the outdated content for the file beacuse we read the old content before we overwrite it with more content
        if dir == FILENAME:
            # Skipping our file if found in any dir or subdirs.
            # If we where to protect on multilayer like
            #
            # └── documents
            #     ├── .protection
            #     ├── work
            #     │   ├── .protection
            #     │   ├── project_alpha
            #     │   │   ├── notes.txt
            #     │   │   └── data
            #     │   │       └── results.csv
            #     │   └── project_beta
            #     │       └── presentation.pptx
            #     └── personal
            #         └── recipes.txt
            # In this case the .protection file in work will keep the data of
            # project_alpha/notes and project_alpha/data/results.csv checked
            # And the .protection file in documents will keep these and also personal/recipes.txt safe too.
            # Saving the data of the protection file would be redundant witch depends on the person wether that is good or not
            continue
        # Checks that the object we found in the current dir is a file
        if os.path.isfile(new_path):
            # If it is a file then we add the path to the files we have found so far
            files.append(new_path)
        # if it is not a file we assume that it is a dir,
        # this should technically handle other cases like that it currently does follow symlinks
        # if it is a mount then it will try to walk it.
        else:
            # Recurivly finds all the files in the new path that we have found is a directory or a symlink
            files.extend(find_files(new_path))
    # Returns the files
    return files


# Convenience method for hashing the content of the file from a path to the file
def hash_file_content(path):
    """
    This function will read the content as bytes so that it works regardless of encoding scheme it will then hash it and return the hexadecimal representation of the hash

    params:
    path: string that is a correctly formatted path to a file

    returns:
    hexadecimal representation of the sha512 hash
    """
    # Opens the file using `with` so that it is closed after a return
    with open(path, "rb") as f:
        # Reads the content of the file
        content = f.read()
        # Hashes the content and retuns it encoded as hexadecimal in a string. When we return here it will close the filehandler aswell
        return hashlib.sha512(content).hexdigest()

# Reads the new data from the root dir
def reads_new_data(root_dir):
    """
    This function reads all the files and then generates hashes for the files
    params:
    root_dir: string that is a correctly formatted path to the exact starting location where we are protecting

    returns:
    A dict with the keys being the filepaths and the values being the hashes of the respective content
    or Null if it is not a directory
    """
    # Ensures that the root_dir exists and also is a directory
    if os.path.isdir(root_dir):
        # Finds all the filepaths in this directory and its subdirectories
        files = find_files(root_dir)
        # Defaults for the result is an empy dict
        res = {}
        # Loops over all the filepaths
        for filepath in files:
            # Creats a dict with the filepath as the key and the hash as the value
            res[filepath] = hash_file_content(filepath)
        # Returns the result
        return res
        # If it is not a directory then we raise an Exception
    else:
        # Raise an error if it this directory is not indead a correct
        raise("Root dir is not a directory")

# Reads the old file to collect it to usefull data
def read_old_data(root_path):
    # data is initalized empty.
    data = {}
    # Gets the .protection filepath
    prot_file = protection_file(root_path)
    # if it exists we read it otherwise there was no previous data so we return the empty data
    if os.path.exists(prot_file):
        # This can not fail beacuse we know that it exist. Opens the data with `open` so that it is closed when not used
        with open(os.path.join(prot_file), "r") as f:
            # Reads line for line
            for line in f.readlines():
                # ensures that the line is not empty beacuse then we skipp it
                if not line == "\n":
                    # beacuse sha512 is 512 bytes that is 128 Bytes
                    # This gets the content from 0 to 128 bytes (the hash)
                    hash = line[:128]
                    # This part gets the rest of the content len(line)-1 ensures that we compensate for len being 1 indexed
                    path = line[128:len(line) - 1]
                    # Inserts it to the dictonary with the path as the key and the hash as the value
                    data[path] = hash
            #returns the data after having read all lines
            return data
    # If the folder does not exist
    else:
        # We return the empy data
        return data

# Writes over the old data of changed files
def save_data_to_file(root_dir, data):
    # converst the dict of data too lines that we can insert
    lines = dict_to_lines(data)
    # Opens the protection file with write and also writes over beacuse "w" truncates the file
    with open(protection_file(root_dir), "w") as f:
        # writes the lines to the file
        f.writelines(lines)

# Formats the dict to lines that we can store
def dict_to_lines(data):
    # If there is no data then default is no lines
    lines = []
    # for eatch path and hash in the data
    for path, hash in data.items():
        # appends lines to the file crusially putting the hash first as that is a known size and then putting a newline in the end so that we know when the data is finished
        lines.append(hash + path + "\n")
    # Returns the formated lines
    return lines

# Create the diffs of the file given an old and a new
def diff_dicts(old, new):
    # Creates a set of the keys for the old and new dict
    # Sets ensure that at no time are there duplicats thus enabling set theorymathematics
    old_keys = set(old.keys())
    # Same for the new dict
    new_keys = set(new.keys())
    # This gets the shared keys in the sets(thus the ones that are not deleted nor added)
    # Mathematically this is a union N ∩ O
    shared_keys = old_keys.intersection(new_keys)
    # Gets the keys that are in the new but not in the old
    # Mathematically this is N\O
    # This is the added files, the ones that did not exist but do now
    added = new_keys-old_keys
    # Gets the keys that are in the old but not in the new
    # Mathematically this is O\N
    # This is the deleted files, the ones that used to exist
    deleted = old_keys-new_keys
    # We create a new set to find all the ones that are changed
    changed = set()
    # For all the keys that are shared we need to know whether they have been modified
    for key in shared_keys:
        # If the hash of the new file content and the old file content are diffrent then they are not the same
        if old[key] != new[key]:
            # We add the changed files to the set
            changed.add(key)
    # Returns the set off added changed or deleted keys
    return (added, changed, deleted)


def main():
    print("Hello and welcome to the wierd IDS when you wish you could use git :)")
    # First print our promt to get the directory
    print("What is the root dir to protect")
    # Get the root_directory too check from the user
    root_dir = input("")
    # If it is not a directory(so a file or nonexisting)
    if not os.path.isdir(root_dir):
        # Then we print that this is not a directory
        print("This is not a directory, try again")
        # And return so we dont print anything stupid
        return
    # We read the old data file before the new so that we can not screw up writing over it
    old_data = read_old_data(root_dir)
    # We traverse the directory and its subdirectories
    new_data = read_new_data(root_dir)
    # We get the new, changed and deleted keys by diffing the dicts of data
    (new, changed, deleted) = diff_dicts(old_data, new_data)
    # To print it better we convert it to a list
    sorted_new = list(new)
    # We then sort it
    sorted_new.sort()
    # For better printing see `sorted_new` comment
    changed_new = list(changed)
    # We sort it
    changed_new.sort()
    # For better printing see `sorted_new` comment
    deleted_new = list(deleted)
    # We sort it
    deleted_new.sort()
    #Formating, start of report
    print("REPORT")
    # cool line to separate
    print("------")
    # We check if there was any changes to the report, and if it was not then we shortcurcit
    if len(new) == 0 and len(changed) == 0 and len(deleted) == 0:
        # We inform the user that they are safe for now
        print("There where no changes in the folder, you are safe for now")
        # we return so we again dont print anything stupid
        return
    # Print a new line for separation
    print()
    # Print the new files added 👀 WARNING
    print("NEW FILES")
    # cool line to separate
    print("---------")
    # We split the filepaths with a newline so that it looks cool
    print("\n".join(sorted_new))

    # Print a new line for separation
    print()
    # Print the files that where changed 👀 WARNING
    print("CHANGED FILES")
    # cool line to separate
    print("-------------")
    # We split the filepaths with a newline so that it looks cool
    print("\n".join(changed_new))
    # Print a new line for separation
    print()
    # Print the files that where removed 👀 WARNING
    print("REMOVED FILES")
    # cool line to separatea
    print("-------------")
    # we split the filepaths with a newline so that it looks cool
    print("\n".join(deleted_new))
    # we now save that data over the old data
    save_data_to_file(root_dir, new_data)
    # then exist

# If the file is not main then dont run it
if __name__ == "__main__":
    # run the main function
    main()
