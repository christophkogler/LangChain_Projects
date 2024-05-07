#chainlit_general_chatbot.py
#Requires RAG dockerfile build.

#   ------------------------------------- INCOMPLETE -----------------------------------------
#   Using chainlit for ui. Chat with a user. Use the chat history as context; include a file if requested. 
#   This script requires the following packages to be installed: langchain ollama chainlit pathlib
#   This script will not execute properly if called via 'python <file path>'. Execute it using 'chainlit run <file path>'
#   This script assumes Ollama is being served.

from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ChatMessageHistory
import chainlit as cl
from common_utils import summarizing_mistral, creative_mistral
import subprocess
from chainlit_utils import get_file_path

all_messages = ChatMessageHistory()
all_messages.add_message(("system", """You are a helpful AI assistant."""))

@cl.on_chat_start
async def on_chat_start():
    creative_mistral_endpoint = Ollama(**creative_mistral)
    output_parser = StrOutputParser()
    
    #Set up our (lang)chain(s) for this chat...
    #
    chatbot = ChatPromptTemplate.from_template("""{chat_history}

{input}""")
    chatbot_chain = chatbot | creative_mistral_endpoint | output_parser
    cl.user_session.set("chatbot_chain", chatbot_chain)
    #
    file_and_chat = ChatPromptTemplate.from_template("""{chat_history}

<working_file>
{input_file}
</working_file>

{input}""")
    file_and_chat_chain = file_and_chat | creative_mistral_endpoint | output_parser
    cl.user_session.set("file_and_chat_chain", file_and_chat_chain)
    #Chain for getting user intention: load/change file, or chatting normally?
    determine_user_intention = ChatPromptTemplate.from_messages([
        ("system", """You are acting as a decision making system for an AI chatbot. Based on the input from the user, determine what they want. If they indicate an intention to load a file or change the loaded file, respond with only the words 'LOAD FILE'. If they are attempting to do anything else, respond with only the words 'CHAT NORMALLY'. Do not respond with anything besides one of those two phrases."""),
        ("human", """{input}""")
    ])
    deterministic_mistral_endpoint = Ollama(**summarizing_mistral)
    determine_intention_chain = determine_user_intention | deterministic_mistral_endpoint | output_parser
    cl.user_session.set("determine_intention_chain", determine_intention_chain)
    await cl.Message("How can I help?").send()

@cl.on_message
async def on_message(message: cl.Message):
    chatbot_chain = cl.user_session.get("chatbot_chain")
    file_and_chat_chain = cl.user_session.get("file_and_chat_chain")
    determine_intention_chain = cl.user_session.get("determine_intention_chain")
    #On each message,
        #Add the new incoming message to the chat history.
        #Choose how to handle the message.
        #Get chain response, add to chat history.
    user_input = message.content
    
    #all_messages.add_user_message(user_input)
    
    #Determine user intentions; load a/change loaded file? Converse / instructions?
    determine_intention_invoke_dict = {"input":user_input}
    print("Starting intention chain invoke.")
    intention = (await determine_intention_chain.ainvoke(determine_intention_invoke_dict)).replace(" ","")
    print("Intention:%s" % intention)
    if intention.startswith("LOADFILE"):
        file_path = await get_file_path()
        cl.user_session.set("input_file", file_path)
        return
    
    targetfile = cl.user_session.get("input_file")
    
    response = "YOU SHOULD NEVER SEE THIS TEXT."
    #if a target file is set, use 'chat and file'; else, use 'chat'
    if targetfile:
        with open(targetfile, 'r') as file:
            input_file_contents = file.read()

        file_and_chat_invoke_dict = {
            "chat_history":all_messages.messages,
            "input_file":input_file_contents,
            "input":user_input,
        }
        print("Starting file-chatbot chain invoke.")
        response = await file_and_chat_chain.ainvoke(file_and_chat_invoke_dict)
    else:
        chatbot_invoke_dict = {
            "chat_history":all_messages.messages,
            "input":user_input,
        }
        print("Starting chatbot chain invoke.")
        response = await chatbot_chain.ainvoke(chatbot_invoke_dict)
        
    print("Response:%s" % response)
    print("Adding response to history.")
    all_messages.add_ai_message(response)
    print("Sending response message.")
    await cl.Message(response).send()
    print("End of onMessage handling.")