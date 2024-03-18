THE FOLLOWING INFORMATION IS MACHINE GENERATED.
IT MAY CONTAIN INCONSISTENCIES OR INACCURACIES.

# RAG  

**Description:** The RAG directory contains the primary resources and configurations for a Python application using Retrieveal Augmented Generation (RAG). It includes a `Dockerfile` defining steps to build a container image with necessary dependencies, such as NVIDIA Container Toolkit, Ollama, LangChain, BeautifulSoup, ChromaDB, cmake, unstructured, and specific Natural Language Toolkit packages. The Ollama models are stored in the `/myapp/LLM-models` directory within the container image.

 ## Dockerfile

**Description:** This file outlines the steps to build a Python-based container image for Retrieveal Augmented Generation (RAG). It starts from a base Python image, installs necessary dependencies including NVIDIA Container Toolkit for GPU passthrough and Ollama for LLM serving. Additionally, it installs LangChain, BeautifulSoup, ChromaDB, cmake, unstructured, and some Natural Language Toolkit packages. The Ollama models directory is mounted to `/myapp/LLM-models`.