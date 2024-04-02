import json
import sys
import os


def get_from_disk(file):
    # yield lines from the file
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            yield line


def load_to_disk(file_path, index: list, mode="w"):
    # makes a list of key-value pairs to a file on disk 
    with open(file_path, mode, encoding="utf-8") as file:
        for key, value in index:
            file.write(get_format(key, value))


def save_to_json_disk(file_path, data: list, indent_value=4, mode="w"):
    # saves data to JSON file on disk
    with open(file_path, mode, encoding="utf-8") as file:
        json.dump(dict(data), file, indent=indent_value)


def load_json_from_disk(file_path):
    # loads JSON data from file on disk
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def getsizeof_in_bytes(item):
    # calculates the size of an item in bytes
    return sys.getsizeof(item)


def getsizeof_in_MB(item):
    # converts size of an item from bytes to megabytes
    return getsizeof_in_bytes(item) / (1024 * 1024)


def clear_folder(folder_path):
    # List all files in the folder
    if not os.path.isdir(folder_path):
        return

    files = os.listdir(folder_path)

    # Iterate over each file and delete it
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            remove_file(file_path)
        elif os.path.isdir(file_path):
            clear_folder(file_path)  # Recursively clear subdirectories


def remove_file(file_path):
    # removes file from disk
    os.remove(file_path)


def create_folder(folder_path):
    # creates folder at folder_path
    os.makedirs(folder_path)


def get_format(key, value: list):
    # formats key-value pair as a string
    return f'{key}: {", ".join(str(x) for x in value)}\n'


def find_longest_folder(main_folder_path):
    # finds subfolder within a given folder that contains the most files
    folders = os.listdir(main_folder_path)
    max_length = 0
    folder_name = ""
    for folder in folders:
        path = os.path.join(main_folder_path, folder)
        subfiles = os.listdir(path)
        if len(subfiles) > max_length:
            max_length = len(subfiles)
            folder_name = folder
    print(max_length, folder_name)