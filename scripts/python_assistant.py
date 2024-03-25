#code_assistant.py
#Requires RAG dockerfile build.

#   ------------------------------------- INCOMPLETE -----------------------------------------
#   Using a directory as context, read a file, then act as a coding assistant : answer questions, suggest changes, etc.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs]

#Imports
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import common_utils

def import_assistant(targetfile, task_input):
    #This coding assistant is an LLM which will:
    #Read the file found at targetfile, list imports, check each import for use, return a list of missing or unused imports.

#The System message...
    system_message = SystemMessagePromptTemplate.from_template("""You are a helpful AI assistant and an expert in Python code.
Solve the provided task using your coding and language skills.

Suggest the minimal changes to the provided file required in order to complete the task.""")
#Task and context...
    task_and_file = ChatPromptTemplate.from_template("""Task: {input}
    
<working_file>
{input_file}
</working_file>""")
#Create the final prompt.
    final_prompt = ChatPromptTemplate.from_messages([
        system_message,
        task_and_file, 
    ])

    #The LLM which will serve this prompt.
    ollama_endpoint = Ollama(**common_utils.summarizing_mistral)
    #Parse the output back into a string.
    output_parser = StrOutputParser()
    #Final chain.
    general_taskable_chain = final_prompt | ollama_endpoint | output_parser

    with open(targetfile, 'r') as file:
        input_file = file.read()

    general_task_invoke_dict = {
        "input_file":input_file,
        "input":task_input,
    }

    response = general_taskable_chain.invoke(general_task_invoke_dict)
    
    return (response)

file_path = common_utils.get_file_path()

print(import_assistant(file_path, task_input))