#chromadb_utils.py

#   Provides a few chromadb convenience utilities.
#   This script requires the following packages to be installed: langchain ollama beautifulsoup4 cmake unstructured[alldocs] pathlib

from langchain_community.vectorstores import Chroma

def purify_db():
    # Purify the DB of vectors.
    chromadb = Chroma()
    ids = chromadb.get()['ids']
    if len(ids) > 0:  # Check if there is at least one ID
        chromadb.delete(ids)
        
summarizing_mistral = {
    "model": "mistral:instruct",
    "temperature": 0.0,
    "mirostat": 2,
    "mirostat_eta": .2,
    "mirostat_tau": 5.0,
    "tfs_z": 2,
    "top_k": 10,
    "top_p": 0.5
}