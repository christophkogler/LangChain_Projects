THE FOLLOWING INFORMATION IS MACHINE GENERATED.
IT MAY CONTAIN INCONSISTENCIES OR INACCURACIES.

# RAG  

**Description:** The RAG directory contains the primary resources and configuration files for building and running a Python application using Docker. It includes a `Dockerfile` that sets up a Python container image with additional dependencies such as NVIDIA Container Toolkit, Ollama, BeautifulSoup, ChromaDB, cmake, unstructured, and pathlib. The Ollama models directory is located within the container at `/myapp/LLM-models`.

 ## Dockerfile

**Description:** This file outlines the steps to build a Python container image with additional dependencies. It starts from a base Python image, installs necessary tools like NVIDIA Container Toolkit for GPU passthrough and Ollama for LLM serving. Additionally, it installs packages such as BeautifulSoup, ChromaDB, cmake, unstructured, and pathlib. The Ollama models directory is mounted to `/myapp/LLM-models` within the container.