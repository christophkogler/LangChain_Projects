#chromadb_utils.py

#   Provides a few chromadb convenience utilities.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs] pathlib

from langchain_community.vectorstores import Chroma

def purify_db():
    # Purify the DB of vectors.
    ids = Chroma().get()['ids']
    if len(ids) > 0:  # Check if there is at least one ID
        chromadb.delete(ids)
        
summarizing_mistral = {
    "model": "mistral:instruct",
    #"num_ctx": 4096,
    "temperature": 0.0,
    "mirostat": 2,
    "mirostat_eta": .2,
    "mirostat_tau": 5.0,
    "tfs_z": 2,
    "top_k": 10,
    "top_p": 0.5
}

def get_file_path():
    # Get directory and file name...
    working_directory = input("What directory will we be working in? ") or "/myapp/LangChain_Projects/"
    filename = input("What is the name of the file you want to work on? ") or "BAD FILE NAME RESPONSE"
    
    # Get the file(s)...
    start_dir = Path(working_directory)
    all_files_named_filename = start_dir.rglob(filename)
    
    # Generate paths list...
    paths = [file.resolve() for file in all_files_named_filename]

    # Handle based on amount of files found.
    if len(paths) == 0:
        print(f"No files named '{filename}' were found within {working_directory} or any sub-directory. Perhaps you entered the wrong file name, or started in the wrong directory?")
        return get_file_path()
    
    if len(paths) == 1:
        print(f"Found a file at '{paths[0]}'.")
        return paths[0]
    
    # Else, print paths as a numbered list, select based on user input.
    if len(paths) > 1:
        file_select_string = f"Multiple files named '{filename}' found:\n"
        for i, path in enumerate(paths):
            file_select_string += f"{i + 1}. {path}\n"
        file_select_string += "\nEnter the number of the file you want to select: "
        
        def select_file_recurse():
            try:
                print(file_select_string, end='')
                file_select_input = int(input())
                if file_select_input > len(paths) or file_select_input < 1:
                    print("Invalid input. Please enter a valid number.")
                    return select_file_recurse()
                return paths[file_select_input - 1]
            except ValueError:
                print("Invalid input. Please enter a number.")
                return select_file_recurse()
        
        selected_file = select_file_recurse()
        return selected_file
