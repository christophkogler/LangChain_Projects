#chainlit_python_assistant.py
#Requires RAG dockerfile build.

#   ------------------------------------- INCOMPLETE -----------------------------------------
#   Using chainlit for ui. Take in a file, chat with user to solve problems / complete tasks / etc related to file.
#   This script requires the following packages to be installed: langchain ollama chainlit pathlib

from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ChatMessageHistory
import chainlit as cl
#from chainlit import AskUserMessage
from pathlib import Path
from common_utils import summarizing_mistral

#Get file path as a string
async def get_file_path():
    #Get directory and file name...
    dir_request = "What directory will we be working in?"
    dir_response = await cl.AskUserMessage(content=dir_request).send()
    working_directory = dir_response["output"]
    if not working_directory:
        working_directory = "/myapp/LangChain_Projects/"
    filename_request = "What is the name of the file you want to work on?"
    fileresponse = await cl.AskUserMessage(content=filename_request).send()
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

all_messages = ChatMessageHistory()
all_messages.add_message(("system", """You are a helpful AI assistant and an expert in Python code.
Solve the provided task using your coding and language skills.

Suggest the minimal changes to the provided file required in order to complete the task."""))


@cl.on_chat_start
async def on_chat_start():
    await cl.Message("Remember to serve Ollama!").send() # Remind user to ollama serve
    input_file = await get_file_path()                         # Get file path...
    #Set up our langchain for this chat...
    #Prompt template.
    task_and_file = ChatPromptTemplate.from_template("""    
<working_file>
{input_file}
</working_file>

{input}""")
    #The LLM which will serve this prompt.
    ollama_endpoint = Ollama(**summarizing_mistral)
    #Parse the output back into a string.
    output_parser = StrOutputParser()
    #Final chain.
    chain = task_and_file | ollama_endpoint | output_parser
    cl.user_session.set("chain", chain)
    cl.user_session.set("input_file", input_file)
    await cl.Message("What would you like to do with this file?").send()
    

@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("chain")
    targetfile = cl.user_session.get("input_file")
    #On each message,
        #Add the new incoming message to the chat history.
        #Insert message & the file contents, for invoke.
        #Get chain response, add to chat history.
    user_input = message.content
    
    all_messages.add_user_message(user_input)
    
    with open(targetfile, 'r') as file:
        input_file_contents = file.read()

    invoke_dict = {
        "input_file":input_file_contents,
        "input":user_input,
    }
    
    response = chain.invoke(invoke_dict)
    all_messages.add_ai_message(response)
    await cl.Message(response).send()