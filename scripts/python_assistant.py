#code_assistant.py
#Requires RAG dockerfile build.

#   ------------------------------------- INCOMPLETE -----------------------------------------
#   Using a directory as context, read a file, then act as a coding assistant : answer questions, suggest changes, etc.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs] pathlib

#Imports
import langchain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import pathlib
import common_utils

#Code

def import_assistant(targetfile):
    #This coding assistant is an LLM which will:
    #Read the file found at targetfile, list imports, check each import for use, return a list of missing or unused imports.

    coding_llm = {
        "model": "deepseek-coder:6.7b",
        #"verbose": True,
        "temperature": 0.5,
        "mirostat": 2,
        "mirostat_eta": 0.1,
        "mirostat_tau": 5.0,
        #"tfs_z": 2,
        #"top_k": 50,
        #"top_p": 0.7
    }
    
#Chaing to create import lists.
    #Create the prompt.
    list_imports = ChatPromptTemplate.from_template("""Create a numbered list of the imports in the following file. Do nothing else.
    
{input_file}""")
    #The LLM which will serve this prompt.
    ollama_endpoint = Ollama(**common_utils.summarizing_mistral)
    #Parse the output back into a string.
    output_parser = StrOutputParser()
    #Final chain.
    list_imports_chain = list_imports | ollama_endpoint | output_parser

#Create a 1-shot example:
    with open("/myapp/LangChain_Projects/scripts/basic_retriever.py", 'r') as file:
        example_file = file.read()
        
    one_shot_example_list_import_invoke_dict = {
        "input_file":example_file
    }
    example_import_list = list_imports_chain.invoke(one_shot_example_list_import_invoke_dict)
    one_shot_example_prompt = ChatPromptTemplate.from_messages(
        [('human', """Create a numbered list based on the provided list of imports. For each import, find a line in the file where the import was used, either to get a variable or to call a function, and copy the line letter for letter. If you cannot find any place where the import is used, say "___ was unused."
<imports>
{example_import_list}
</imports>

<input_file>
{example_file}
</input_file>"""), 
        ('ai', """1: import langchain - langchain was unused.
2: from langchain.chains import create_retrieval_chain - retrieval_chain = create_retrieval_chain(retriever, document_chain)
3: from langchain.chains.combine_documents import create_stuff_documents_chain - create_stuff_documents_chain was unused.
4: from langchain_core.prompts import ChatPromptTemplate - prompt = ChatPromptTemplate.from_template(...)
5: from langchain_community.document_loaders import WebBaseLoader - loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide") #Select a particular webpage
6: from langchain_community.embeddings import OllamaEmbeddings - embeddings = OllamaEmbeddings(model="mistral:instruct")
7: from langchain_community.vectorstores import Chroma - vector = Chroma.from_documents(documents, embeddings) 
8: from langchain_community.llms import Ollama - mistral_instruct = Ollama(model="mistral:instruct")
9: from langchain_text_splitters import RecursiveCharacterTextSplitter - text_splitter = RecursiveCharacterTextSplitter()""")]
    )
    

    
    with open(targetfile, 'r') as file:
        input_file = file.read()

    list_import_invoke_dict = {
        "input_file":input_file
    }

    import_list = list_imports_chain.invoke(list_import_invoke_dict)
    print (import_list)
    
    check_imports = ChatPromptTemplate.from_template("""Create a numbered list based on the provided list of imports. For each import, find a line in the file where the import was used, either to get a variable or call a function, and copy the line letter for letter. If you cannot find any place where the import is used, say "___ was unused."
</imports>
{imports}
</imports>

<input_file>
{input_file}
</input_file>""")
    
    
    #Create the final prompt.
    final_prompt = ChatPromptTemplate.from_messages([
        one_shot_example_prompt,
        check_imports, 
    ])

    #Re-using string parser.
    #The LLM which will serve this prompt.
    ollama_endpoint = Ollama(**common_utils.summarizing_mistral)
    #Final chain.
    check_imports_chain = final_prompt | ollama_endpoint | output_parser
    
    check_import_invoke_dict = {
        "input_file":input_file,
        "imports":import_list,
        "example_import_list":example_import_list,
        "example_file":example_file,
    }
    
    import_usage_list = check_imports_chain.invoke(check_import_invoke_dict)
    
    #print (import_usage_list)
    
    return (import_usage_list)
    

print(import_assistant("/myapp/LangChain_Projects/scripts/file_summarizer.py"))