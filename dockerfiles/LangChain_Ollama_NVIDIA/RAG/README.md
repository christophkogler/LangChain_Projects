THE FOLLOWING INFORMATION IS MACHINE GENERATED.
IT MAY CONTAIN INCONSISTENCIES OR INACCURACIES.

# RAG  

**Description:**  The RAG directory contains the primary resources and configuration files for building and running a Python application using Docker. It includes a `Dockerfile` that sets up a Python container image with additional dependencies such as NVIDIA Container Toolkit, Ollama, BeautifulSoup, ChromaDB, cmake, unstructured, and pathlib. The Ollama models directory is located within the container at `/myapp/LLM-models`.

 ## Dockerfile

**Description:** This `Dockerfile` provides instructions to build a Python container image with additional dependencies installed. It starts from a base Python image, sets up GPU passthrough using NVIDIA Container Toolkit, installs Ollama for LLM serving, and includes required packages such as BeautifulSoup, ChromaDB, cmake, unstructured, and pathlib. The Ollama models directory is mounted to `/myapp/LLM-models`.