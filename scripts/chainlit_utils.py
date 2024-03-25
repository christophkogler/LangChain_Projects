import chainlit as cl
from pathlib import Path

#Get file path as a string
async def get_file_path():
    #Get directory and file name...
    dir_request = "What directory will we be working in?"
    dir_response = await cl.AskUserMessage(content=dir_request).send()
    if dir_response:
        working_directory = dir_response["output"]
    else:
        working_directory = "/myapp/LangChain_Projects/"
    filename_request = "What is the name of the file you want to work on?"
    fileresponse = await cl.AskUserMessage(content=filename_request).send()
    if fileresponse:
        filename = fileresponse["output"]
    else:
        filename = "BAD FILE NAME RESPONSE"
    
    filename = fileresponse["output"]
    #Get the file(s)...
    start_dir = Path(working_directory)
    all_files_named_filename = start_dir.rglob(filename)
    #Generate paths list...
    paths = []
    for file in all_files_named_filename:
        paths.append(file.resolve())
    #Handle based on amount of files found.
    if len(paths) == 0:
        no_files_response = "No files named '%s' were found within %s or any sub-directory. Perhaps you entered the wrong file name, or started in the wrong directory?" % (filename, working_directory)
        await cl.Message(content=no_files_response).send()
        return await get_file_path()
    if len(paths) == 1:
        await cl.Message("Found a file at '%s'." % paths[0]).send()
        return paths[0]
    #Else, print paths as a numbered list, select based on user input.
    if len(paths) > 1:
        file_select_string = ("Multiple files named '%s' found:\n" % filename)
        for i, (path) in enumerate(paths):
            file_select_string.append(f"{i+1}. {path}")
        file_select_string.append("\nEnter the number of the file you want to select: ")
        
        async def select_file_recurse():
            file_select_response = await cl.AskUserMessage(content=file_select_string).send()
            file_select_input = int(file_select_response["output"])
            if file_select_input > len(paths) or user_input < 1:
                await cl.Message("Invalid input. Please enter a valid number.").send()
                return select_file_recurse()
            return paths[user_input-1]
        selected_file = await select_file_recurse()
    return selected_file