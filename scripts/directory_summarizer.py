#directory_summarize.py
#Requires RAG dockerfile build.

#   Analyzes files, then summarizes the general purpose and contents of a directory.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs] pathlib

import langchain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import pathlib
from file_summarizer import summarize_file
import common_utils

def summarize_directory(directory_name, base_path = "/myapp/"):
    cur_dir_path = base_path + directory_name + "/"
    print("Summarizing %s!" % cur_dir_path)
    #Make sure the Ollama server is running. After that, you can do:
    model_name = "mistral:instruct"
    mistral_instruct = Ollama(**common_utils.summarizing_mistral)
    
    path_dir = os.listdir(cur_dir_path)
    
    files, directories = [], []
    for file in path_dir:
        files.append(file) if not os.path.isdir(os.path.join(cur_dir_path, file)) else directories.append(file)
    
    summaries = []
    
    ignore_files_named = [
        "README.md",
    ]
    
    files = [file for file in files if file not in ignore_files_named]
    
    ignore_dirs_named = [
        "__pycache__",
        ".git",
    ]
    
    directories = [dir for dir in directories if dir not in ignore_dirs_named]
    
    for file_name in files: # Summarize each file.
        result = summaries.append(summarize_file(file_name, cur_dir_path))
        if result is not None:
            summaries.append(result)
    
    for subdir_name in directories: # Recursively summarize any sub-directories.
        result = summarize_directory(subdir_name, cur_dir_path)
        summaries.append(result)

    if len(summaries) == 0:
        print("No summaries generated in %s!" % cur_dir_path)

    summary_string = "No files found."
    if len(summaries) > 0:
        summary_string = ""
        summary_string = "\n\n\n".join(summaries)

    # Convert all these strings to a document.
    doc = Document(page_content=summary_string, metadata={"source": "local"})
    
    # Use a text splitter to process the docs.
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents([doc])

    common_utils.purify_db()
    embeddings = OllamaEmbeddings(model=model_name)
    vector = Chroma.from_documents(documents, embeddings) 
    retriever = vector.as_retriever()
    
    directy_summarization_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
    The context provided below contains the summaries of all files and subdirectories in a directory named {input}.
    
    <context>
    {context}
    </context>

    Based on the provided context, write a concise description for the directory {input}.
    
    # {input}
    **Description:**""")
    describe_directory = create_stuff_documents_chain(mistral_instruct, directy_summarization_prompt)
    
    retrieval_chain = create_retrieval_chain(retriever, describe_directory)
    response = retrieval_chain.invoke({"input": directory_name}) # returns a dict, response["answer"]
    directory_summary = "# " + directory_name + "  \n\n**Description:** " + response["answer"]
    
    file_summary_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
    The context provided below contains the summaries of all files and subdirectories in a directory named {input}.
    
    <context>
    {context}
    </context>

    Write a concise Markdown summary for each item in the context above. Each item should have a level 2 heading. Do not describe the contents of any directories explicitly, and instead speak about their purpose.""")
    describe_files_and_folders = create_stuff_documents_chain(mistral_instruct, file_summary_prompt)
    second_retrieval_chain = create_retrieval_chain(retriever, describe_files_and_folders)
    file_and_folder_summary = second_retrieval_chain.invoke({"input": directory_name, "directory_summary": directory_summary})
    
    readme_response = """THE FOLLOWING INFORMATION IS MACHINE GENERATED.
IT MAY CONTAIN INCONSISTENCIES OR INACCURACIES.

%s

%s""" % (directory_summary, file_and_folder_summary["answer"])
    
    with open(cur_dir_path + "README.md", 'w') as file:
        file.write(readme_response)

    print("README generated for directory %s!" % cur_dir_path)
    
    return_response = """%s

%s""" % (directory_summary, file_and_folder_summary["answer"])
    return(return_response)


summarize_directory("LangChain_Projects")