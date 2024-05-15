import os
import sys
import shutil

def find_target_directory(filename, directories):
    def recursive_search(directory_structure, filename):
        for directory_key, subdirectories in directory_structure.items():
            if directory_key in filename:
                if not subdirectories:
                    return directory_key
                else:
                    # search through all subdirectories
                    subdirectory_match = recursive_search(subdirectories, filename)
                    if subdirectory_match:
                        return os.path.join(directory_key, subdirectory_match)
        return None

    return recursive_search(directories, filename)

def move_file(filename, source_path, target_directory):
    source = os.path.join(source_path, filename)
    destination = os.path.join(source_path, target_directory)
    try:
        shutil.move(source, destination)
        print(f"Moved '{filename}' to '{destination}'")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Skipping...")
    except shutil.Error:
        # for when the destination file already exists
        print(f"Warning: File '{filename}' already exists in '{destination}'. Skipping...")

def sort_files(directory_structure, source_path, extensions):
    for root, _, files in os.walk(source_path):
        for filename in files:
            file_extension = filename.split('.')[-1]
            if file_extension in extensions:
                target_directory = find_target_directory(filename, directory_structure)
                if target_directory:
                    move_file(filename, source_path, target_directory)
                else:
                    print(f"Error: File '{filename}' doesn't match any directory structure. Skipping...")
            else:
                print(f"Error: File '{filename}' has an unsupported extension. Skipping...")

def create_directories(path, levels, extensions):
    directories = {}
    if not levels:
        return directories

    if len(levels) == 1:
        for directory in levels[0]:
            new_path = os.path.join(path, directory)
            os.makedirs(new_path, exist_ok=True)
            directories[directory] = {ext: [] for ext in extensions}
            for ext in extensions:
                os.makedirs(os.path.join(new_path, ext), exist_ok=True)
    else:
        for directory in levels[0]:
            new_path = os.path.join(path, directory)
            os.makedirs(new_path, exist_ok=True)
            directories[directory] = create_directories(new_path, levels[1:], extensions)
    return directories

def get_valid_extension_input():
    while True:
        extensions_input = input("Enter all of your file extensions separated by commas (e.g., txt, png): ")
        if ',' not in extensions_input and extensions_input.strip():  # Check for comma and if the input is not blank
            print("Please separate extensions with commas.")
        else:
            return [ext.strip() for ext in extensions_input.split(',')]

def get_valid_level_input(level_number):
    while True:
        input_str = input(f"Enter the names of the {level_number}. level directories separated by commas (leave blank if none): ")
        if not input_str.strip():
            return None
        elif ',' not in input_str:  # Check for comma
            print("Please separate directory names with commas.")
        else:
            return input_str.strip().split(',')

# check if TO_SORT folder exists, create if it doesn't, check if empty
def handle_to_sort_folder():
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    to_sort_path = os.path.join(script_dir, "TO_SORT")
    if not os.path.exists(to_sort_path):
        os.makedirs('TO_SORT')
        print("The 'TO_SORT' folder was created. Please copy your files into it and rerun the script.")
        input("Press Enter to exit...")
        return False
    else:
        if not os.listdir(to_sort_path):
            print("The 'TO_SORT' folder is empty. Please copy your files into it and rerun the script.")
            input("Press Enter to exit...")
            return False
        else:
            return True

to_sort_ready = handle_to_sort_folder()

if to_sort_ready:
    extensions = get_valid_extension_input()
    # define the directory structure and create folders
    level_directories = []
    i = 1
    while True:
        level_input = get_valid_level_input(i)
        if not level_input:
            break
        level_directories.append(level_input)
        i += 1

    # Root path for "TO_SORT" folder
    script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    to_sort_path = os.path.join(script_dir, "TO_SORT")

    # Create directories 
    directories = create_directories(to_sort_path, level_directories, extensions)

    # Sort files
    sort_files(directories, to_sort_path, extensions)

    # Rename the "TO_SORT" directory to "SORTED_FILES"
    sorted_files_path = os.path.join(script_dir, "SORTED_FILES")
    os.rename(to_sort_path, sorted_files_path)
    print(f"You can find your files sorted in 'SORTED_FILES'")
    input("Press Enter to exit...")