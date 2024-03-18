#	Additional dependencies to faccilitate Retrieveal Augmented Generation.

#	Starting from a base Python image...
FROM python

#	Pull, update, install, and configure the NVIDIA Container Toolkit (for GPU passthrough)...
RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
	gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && \
	curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
	sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
	tee /etc/apt/sources.list.d/nvidia-container-toolkit.list && \
	apt-get update && \
	apt-get install -y nvidia-container-toolkit && \
	nvidia-ctk runtime configure --runtime=docker

#	Install Ollama (for LLM serving)...
RUN curl -fsSL https://ollama.com/install.sh | sh

#	Install LangChain, BeautifulSoup (for internet browsing), and ChromaDB(for vector storage)...
RUN pip install langchain beautifulsoup4 chromadb

#	Set Ollama models directory to /myapp/LLM-models
ENV OLLAMA_MODELS=/myapp/LLM-models

#	Install cmake (for "unstructued[alldocs]")...
RUN pip install cmake

#	Install unstructured for file parsing...
RUN pip install "unstructured[alldocs]"
RUN pip install "unstructured[md]"

#	Install pathlib for path-related convenience...
RUN pip install pathlib

#	Pre-download some Natural Language ToolKit packages...
RUN python -c 'import nltk; nltk.download("punkt"); nltk.download("averaged_perceptron_tagger")'

#	Ready to serve LangChain via Ollama!