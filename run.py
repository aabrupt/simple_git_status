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
    This is a custom implementation of os.walk that uses recursion. Keep in mind that this does not handle a base case of a too large directory when using.
    params:
    root_dir: string that is a correctly formatted path

    returns:
    string that is a correctly formatted path
    """
    # The collection of files that will appended to by this function.
    files = []
    # `os.listdir` takes in a path and returns a list of relative paths based on the root_path that is inputted into the function. This list is then looped through using a for-loop.
    for dir in os.listdir(root_path):
        # We rebase the search onto the new directory that is found using the `os.listdir` function.
        new_path = os.path.join(root_path, dir)
        if dir == FILENAME:
            continue
        if os.path.isfile(new_path):
            files.append(new_path)
        else:
            files.extend(find_files(new_path))
    return files


def hash_file_content(path):
    with open(path, "rb") as f:
        content = f.read()
        return hashlib.sha512(content).hexdigest()


def read_new_data(root_dir):
    files = find_files(root_dir)
    res = {}
    for filepath in files:
        res[filepath] = hash_file_content(filepath)
    return res


def read_old_data(root_path):
    data = {}
    prot_file = protection_file(root_path)
    if os.path.exists(prot_file):
        with open(os.path.join(prot_file), "r") as f:
            for line in f.readlines():
                if not line == "\n":
                    hash = line[:128]
                    path = line[128:len(line) - 1]
                    data[path] = hash
    return data


def save_data_to_file(root_dir, data):
    lines = dict_to_lines(data)
    with open(protection_file(root_dir), "w") as f:
        f.writelines(lines)


def dict_to_lines(data):
    lines = []
    for path, hash in data.items():
        lines.append(hash + path + "\n")
    return lines


def diff_dicts(old, new):
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    shared_keys = old_keys.intersection(new_keys)
    added = new_keys-old_keys
    deleted = old_keys-new_keys
    changed = set()
    for key in shared_keys:
        if old[key] != new[key]:
            changed.add(key)
    return (added, changed, deleted)


def main():
    print("What is the root dir to protect")
    root_dir = input("")
    if not os.path.isdir(root_dir):
        print("That is not a directory")
        return
    old_data = read_old_data(root_dir)
    new_data = read_new_data(root_dir)
    (new, changed, deleted) = diff_dicts(old_data, new_data)
    sorted_new = list(new)
    sorted_new.sort()
    changed_new = list(changed)
    changed_new.sort()
    deleted_new = list(deleted)
    deleted_new.sort()
    print("REPORT")
    print("------")
    if len(new) == 0 and len(changed) == 0 and len(deleted) == 0:
        print("There where no changes in the folder")
        return
    print("")
    print("NEW FILES")
    print("---------")
    print("".join(sorted_new))

    print()
    print("CHANGED FILES")
    print("-------------")
    print("\n".join(changed_new))
    print()

    print("REMOVED FILES")
    print("-------------")
    print("\n".join(deleted_new))

    print()
    save_data_to_file(root_dir, new_data)


if __name__ == "__main__":
    main()
