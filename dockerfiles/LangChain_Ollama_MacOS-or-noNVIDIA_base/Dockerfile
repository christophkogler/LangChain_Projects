#  This Dockerfile is intended for individuals without NVIDIA GPU's, as well as for those on MacOS. It does not have GPU passthrough.

#  Starting from a base Python image...
FROM python

#  Install LangChain...
RUN pip install langchain

#  Install Ollama...
RUN curl -fsSL https://ollama.com/install.sh | sh

#  Set Ollama models directory to /myapp/LLM-models
RUN export OLLAMA_MODELS = /myapp/LLM-models

#  Ready to serve LangChain via Ollama!
