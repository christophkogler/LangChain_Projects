#directory_summarize.py
#Requires RAG dockerfile build.

#   Recursively analyse subdirectories and files within a directory. Generate a readme for all subdirectories.
#   This script requires the following packages to be installed: langchain ollama pathlib

import langchain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
import os
import pathlib
from file_summarizer import summarize_file
import common_utils
import subprocess

#Why use vectorstores at all? Until I start running into context size issues, let's just insert the summary string(s). 
#from langchain.chains import create_retrieval_chain
#from langchain.chains.combine_documents import create_stuff_documents_chain
#from langchain_community.embeddings import OllamaEmbeddings
#from langchain_community.vectorstores import Chroma
#from langchain_community.document_loaders import TextLoader
#from langchain.schema.document import Document
#from langchain_text_splitters import RecursiveCharacterTextSplitter


# Serve Ollama, and feed outputs & errors to variables in order to keep console clean.
process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def summarize_directory(directory_name, base_path = "/myapp/"):
    common_utils.purify_db()
    cur_dir_path = base_path + directory_name + "/"
    print("Summarizing %s!" % cur_dir_path)
    #Make sure the Ollama server is running. After that, you can do:
    model_name = "mistral:instruct"
    mistral_instruct = Ollama(**common_utils.summarizing_mistral)
    output_parser = StrOutputParser()
    llm_and_output_parser = mistral_instruct | output_parser
    
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
        ".github",
    ]
    
    directories = [dir for dir in directories if dir not in ignore_dirs_named]
    
    for subdir_name in directories: # Recursively summarize any sub-directories.
        result = summarize_directory(subdir_name, cur_dir_path)
        summaries.append(result)
        common_utils.purify_db() 
    
    for file_name in files: # Summarize each file.
        result = summarize_file(file_name, cur_dir_path)
        summaries.append(result)
        common_utils.purify_db() 

    common_utils.purify_db()
    
    if len(summaries) == 0:
        print("No summaries generated in %s!" % cur_dir_path)

    summary_string = "No files found."
    if len(summaries) > 0:
        summary_string = ""
        summary_string = "\n\n\n".join(summaries)

    # Convert all these strings to a document.
    #doc = Document(page_content=summary_string, metadata={"source": "local"})
    
    # Use a text splitter to process the docs.
    #documents = RecursiveCharacterTextSplitter().split_documents([doc])

    #common_utils.purify_db()
    #embeddings = OllamaEmbeddings(model=model_name)
    #vector = Chroma.from_documents(documents, embeddings) 
    #retriever = vector.as_retriever()
    
    directory_summarization_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
Provided below are the summaries of all files and subdirectories in a directory named {input}.
    
<context>
{context}
</context>

Based on the provided summaries, write a concise description for the directory {input}.
    
# {input}
**Description:**""")

    vectorstoreless_summarization_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
Provided below are the summaries of all files and subdirectories in a directory named {input}.
    
<context>
{summaries}
</context>

Based on the provided summaries, write a concise description for the directory {input}.
    
# {input}
**Description:**""")
    simple_directory_summarization_chain = vectorstoreless_summarization_prompt | llm_and_output_parser
    simple_dir_summary_invoke_dict = {
        "input": directory_name,
        "summaries": summary_string,
    }
    response = simple_directory_summarization_chain.invoke(simple_dir_summary_invoke_dict)
    directory_summary = "# " + directory_name + "  \n\n**Description:**" + response
    
    #describe_directory = create_stuff_documents_chain(mistral_instruct, directory_summarization_prompt)
    #retrieval_chain = create_retrieval_chain(retriever, describe_directory)
    #response = retrieval_chain.invoke({"input": directory_name,})
    #directory_summary = "# " + directory_name + "  \n\n**Description:**" + response["answer"]
    
    vectorstoreless_readme_markdown_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
Provided below are the summaries of all files and subdirectories in a directory named {input}.
    
<context>
{summaries}
</context>

Write a concise Markdown summary for each item in the context above. Each item should have a level 2 heading. Do not describe the contents of directories explicitly, and instead speak about their purpose. Omit any mentions of the contents of subdirectories to maintain brevity.""")
    simple_readme_chain = vectorstoreless_readme_markdown_prompt | llm_and_output_parser
    
    simple_readme_invoke_dict = {
        "input": directory_name,
        "summaries": summary_string,
    }
    readme_response = simple_readme_chain.invoke(simple_readme_invoke_dict)
    file_and_folder_summary = readme_response
    
    readme_markdown_prompt = ChatPromptTemplate.from_template("""You are a world class code analyst and technical documentation writer. 
The context provided below contains the summaries of all files and subdirectories in a directory named {input}.
    
<context>
{context}
</context>

Write a concise Markdown summary for each item in the context above. Each item should have a level 2 heading. Do not describe the contents of directories explicitly, and instead speak about their purpose. Omit any mentions of the contents of subdirectories to maintain brevity.""")
    #describe_files_and_folders = create_stuff_documents_chain(mistral_instruct, readme_markdown_prompt)
    #second_retrieval_chain = create_retrieval_chain(retriever, describe_files_and_folders)
    #file_and_folder_summary = second_retrieval_chain.invoke({"input": directory_name, "directory_summary": directory_summary})
    #file_and_folder_summary = file_and_folder_summary["answer"] # response string
    
    #Check if the README starts with our machine_gen_warning; if so, replace it. Otherwise, it's human-made; leave it be.
    machine_gen_warning = """THE FOLLOWING INFORMATION IS MACHINE GENERATED.
IT MAY CONTAIN INCONSISTENCIES OR INACCURACIES."""

    readme_response = """%s

%s 

%s""" % (machine_gen_warning, directory_summary, file_and_folder_summary)

    with open(cur_dir_path + "README.md", 'r') as file:
        input_file = file.read()
        if input_file.startswith(machine_gen_warning):
            with open(cur_dir_path + "README.md", 'w') as file:
                file.write(readme_response)
    
    print("README generated for directory %s!" % cur_dir_path)
    common_utils.purify_db()
    return(directory_summary)


summarize_directory("LangChain_Projects")