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
import subprocess
from chainlit_utils import get_file_path

# Serve Ollama, and feed outputs & errors to variables in order to keep console clean.
process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

all_messages = ChatMessageHistory()
all_messages.add_message(("system", """You are a helpful AI assistant and an expert in Python code.
Solve the provided task using your coding and language skills.

Suggest the minimal changes required in order to complete the task. If any code is to be replaced, copy the original line that is to be replaced, and then write the new code below it."""))

@cl.on_chat_start
async def on_chat_start():
    #await cl.Message("Remember to serve Ollama!").send() # Remind user to ollama serve
    input_file = await get_file_path()                         # Get file path...
    #Set up our langchain for this chat...
    #Prompt template.
    task_and_file = ChatPromptTemplate.from_template("""{chat_history}

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
        "chat_history":all_messages.messages,
        "input_file":input_file_contents,
        "input":user_input,
    }
    print("Starting chain invoke.")
    response = chain.invoke(invoke_dict)
    print("Adding response to history.")
    all_messages.add_ai_message(response)
    print("Sending response message.")
    await cl.Message(response).send()