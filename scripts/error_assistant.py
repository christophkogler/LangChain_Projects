#code_assistant.py
#Requires RAG dockerfile build.

#   ------------------------------------- INCOMPLETE -----------------------------------------
#   This file is intended to take in an error and file and provide instructions on fixing the error.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs] pathlib

import langchain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import pathlib
import common_utils

def coding_assistant(targetfile, example_path):
    #This coding assistant is an LLM which will:
    #Read the file found at targetfile, use example_path as context(?), find docs(???), modify the file as requested, and finally save the edited file.
    
    model_name = "deepseek-coder:6.7b"
    #Make sure the Ollama server is running. After that, you can do:
    coding_mistral = {
        "model": model_name,
        #"verbose": True,
        "temperature": 0.0,
        #"mirostat": 2,
        #"mirostat_eta": 0.0,
        #"mirostat_tau": 5.0,
        #"tfs_z": 2,
        #"top_k": 50,
        #"top_p": 0.7
    }
    
    mistral_instruct = Ollama(**coding_mistral)
    
    common_utils.purify_db()
    embeddings = OllamaEmbeddings(model=model_name)
    files = DirectoryLoader(example_path).load()
    split_files = RecursiveCharacterTextSplitter().split_documents(files)
    vectorstore = Chroma.from_documents(split_files, embeddings)
    retriever = vectorstore.as_retriever()
    
    #Create the prompt.
    code_assistant = ChatPromptTemplate.from_messages([
        ("system", """You are a world class code analyst and programmer. 
    This is what is currently being worked on:
    
    <work_file>
    {input_file}
    </work_file>
    
    """), 
        ("human", """How can I resolve the following error:
    
    {input}""")
    ])
    #Generate "stuff documents" chain, assign a retriever.
    do_coding = create_stuff_documents_chain(mistral_instruct, code_assistant)
    context_retrieval = create_retrieval_chain(retriever, do_coding)
    
    with open(targetfile, 'r') as file:
        input_file = file.read()
        
    #ENTER THE ERROR HERE \/
    error_code = """ """

    response = context_retrieval.invoke({"input": error_code, "input_file":input_file})
    #print(response["answer"])
    
    #with open(cur_dir_path + "README.md", 'w') as file:
        #file.write(readme_response)

    #print("Coding assistant exiting!")
    return (response["answer"])
    

print(coding_assistant("/myapp/LangChain_Projects/scripts/code_assistant.py", "/myapp/LangChain_Projects/scripts/"))