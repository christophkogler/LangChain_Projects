#file_summarizer.py
#Requires RAG dockerfile build.

#   Uses RAG to analyze a file. If it is 'informational', what is about? If it is 'functional', what does it do?
#   This script requires the following packages to be installed: langchain ollama pathlib

import langchain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pathlib
import common_utils
import subprocess

#This file assumes Ollama is being served already; either by the calling script or seperately.

def summarize_file(file_name, current_dir = "/myapp/LangChain_Projects/"):

    common_utils.purify_db()                               
    print("Beginning summarization for %s!" % file_name)
    #Make sure the Ollama server is running. After that, you can do:
    model_name = "mistral:instruct"
    mistral_instruct = Ollama(**common_utils.summarizing_mistral)
    
    #First, let's set up the chain which will take in a question and our retrieved documents and generate the answer.
    prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
    Based on the following context, complete the task below.

    <context>
    {file_content}
    </context>

    Task: Write a concise description for the file '{input}', and do nothing else.

    ## {input}

    **Description:** """)
    output_parser = StrOutputParser()
    
    chain = prompt | mistral_instruct | output_parser
    
    #document_chain = create_stuff_documents_chain(mistral_instruct, prompt)

    #get the first result from recursively searching starting at current_dir for file_name, then get the absolute path in Posix form of that
    target_path = next(pathlib.Path(current_dir).rglob(file_name)).absolute().as_posix()
    
    #print("%s found at %s!" % (file_name, my_path))
    #docs = TextLoader(my_path).load()                           #Load the file.
    
    with open(target_path, 'r') as file:
        input_file_contents = file.read()
    
    if not input_file_contents:                                #Check if the file has any contents.
        return ("The file at %s is empty." % my_path)

    #text_splitter = RecursiveCharacterTextSplitter()
    #documents = text_splitter.split_documents(docs)             #Use a text splitter to process the file.
    #embeddings = OllamaEmbeddings(model=model_name)             #Get the embedding model.
    #vector = Chroma.from_documents(documents, embeddings)       #Use the embedding model to ingest new documents into the vectorstore.
    #print(Chroma().get()['documents'][0])
    #Now that we have this data indexed in a vectorstore, we can create a retrieval chain. 
    #   This type of chain will take an incoming question and dynamically pass the most relevant documents as context, along with the original question.
    #retriever = vector.as_retriever()
    #retrieval_chain = create_retrieval_chain(retriever, document_chain)
    #We can now invoke this chain. This returns a dictionary - the response from the LLM is in the answer key
    
    response = chain.invoke({
        "input": file_name,
        "file_content":input_file_contents,
    })
    
    common_utils.purify_db()   
    return("## "+file_name+"\n\n**Description:** " + response)

#print(summarize_file("Dockerfile"))