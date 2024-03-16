#directory_retrieve.py
#Requires RAG dockerfile build.

#  It implements basic RAG by ingesting documents (a directory) into a Chroma vectorstore.
#  This script requires the following packages to be installed: langchain, ollama, faiss-cpu, beautifulsoup4,

import langchain
from langchain.chains import create_retrieval_chain
#from langchain.chains import VectorDBQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
#from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Make sure the Ollama server is running. After that, you can do:
model_name = "deepseek-coder:6.7b"
mistral_instruct = Ollama(model=model_name)

#First, let's set up the chain which will take in a question and our retrieved documents and generate the answer.
prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")
document_chain = create_stuff_documents_chain(mistral_instruct, prompt)

#---------------- Now let's collect our documents. -------------------

#After installing beautifulsoup4, we can use WebBaseLoader.
#loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide") #Select a particular webpage
#docs = loader.load() #Load the page.

loader = DirectoryLoader('./myapp/LangChain_projects')
docs = loader.load()

# Use a text splitter to process the docs.
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)

#---------------- Next, we need to place them into a vectorstore. ----------------------

#Get the embedding model.
embeddings = OllamaEmbeddings(model=model_name)

#Use the embedding model to ingest documents into the vectorstore.
vector = Chroma.from_documents(documents, embeddings) 

#Now that we have this data indexed in a vectorstore, we can create a retrieval chain. 
#   This type of chain will take an incoming question and dynamically pass the most relevant documents as context, along with the original question.
retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

#We can now invoke this chain. This returns a dictionary - the response from the LLM is in the answer key
response = retrieval_chain.invoke({"input": "Are there any unnecessary imports in the script 'directory_retrieve.py'?"})
print(response["answer"])
