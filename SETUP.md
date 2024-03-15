# Environment Setup
This document is meant to take almost any individual from nothing to being able to run LangChain based Python scripts in a container, with a minimum of both time and effort.  
This brief setup guide will assume you are installing on Windows 10(+) and have an NVIDIA GPU. MacOS and Linux steps should be essentially the same.  

<br/>

### Why _you_ should love Docker  
_Consistency_.  

[Docker](https://www.docker.com/) is a containerization tool that allows getting started in a new environment to be _incredibly_ streamlined via the use of Dockerfiles, which are essentially instructions to building a perfect clone of an environment every time.
It prevents the issue of messy, conflicting package installs or programs leaving junk behind _somewhere_ on your computer.    

Everything stays in the containers, nice and neat. Environments are inherently minimal, and built the exact same way every time.  

<br/>

### Docker Installation
Step 1: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).  
Step 2: Install wsl2 ([Windows Subsytem for Linux 2](https://learn.microsoft.com/en-us/windows/wsl/install)) by running Command Prompt or Powershell **as an Administrator** and entering the following:
```bash
wsl --install
```
Step 3: Restart your computer.  
That should be all you need to do to get Docker Dekstop working!  

#### Storage Warning
If you start collecting a lot of images & containers, or downloading LLM models into the images, Docker can start to use a **lot** of space. The default image save location is in your User.
The image location can be changed at: Settings (the gear in the top right) > Resources > Disk Image Location.  

<br/>

### Setting up the environment using a Dockerfile
After finishing the installation of Docker Dekstop and it's dependencies, you're ready to hit the ground running!  

Creating a new image from a downloaded Dockerfile ([like this one](https://github.com/christophkogler/LangChain_Projects/blob/main/dockerfiles/LangChain_Ollama_NVIDIA_base/Dockerfile)) is simple. Choose a name (in all lowercase, a-z, -, _) and find the path to the directory containing the Dockerfile.  

Then, to create an image named "example" from the Dockerfile in the directory "H:\AI_STUFF\dockerfiles\LangChain_Ollama", you would enter the following into the command line:
```bash
#format
docker buildx build -t <newimagename> <pathtodockerfile> 
#ex: build an image named example
docker buildx build -t example H:\AI_STUFF\dockerfiles\LangChain_Ollama
```
Now you just have to wait for a short while as the image is built, and then you will have a ready-to-go LangChain environment which can be served by Ollama!

<br/>

### Serving Ollama
Now that your image is fully set up, you're ready to start up Ollama and get started experimenting with LangChain.
The command to run a docker image is `docker run ...`, but there are some very useful additional flags that I reccommend using pretty much evey time:  
 - The combined flags `-it` provides an interactive terminal (seemingly required for using shells).
 - The volume flag `-v <host-path>:<container-path>` provides access to external files from within the container.
 - The gpu flag `--gpus all` provides GPU passthroughs for greatly improved LLM performance.
   - works by default on Linux. (unsure)
   - only works on Windows _if_ NVIDIA Container Toolkit is installed (in the container!). This repo's dockerfiles will handle that.
   - the internet says it does _not_ work on MacOS. 🙁 (unsure if still true)
 - The name flag `--name <container-name>` sets the container name to something consistent, instead of two random words.  
```bash
#format
docker run <imagename> <command>
#ex: Starting an image named `langchain_ollama` into an interactive bash shell with container named `active_container`:
docker run -it -v H:/AI_STUFF:/myapp --gpus all --name active_container langchain_ollama /bin/bash
#ex :Starting an image directly into serving models w/ Ollama:
docker run -it -v H:/AI_STUFF:/myapp --gpus all --name active_container langchain_ollama ollama serve
```

### `ollama serve` captures the command line interacting with the container.  
**To interact with the container after serving, start a new command line, and type:**
```bash
docker exec -it <running-container-name> <command>
#ex: start another bash shell in the container
docker exec -it illegible_macguffin /bin/bash
```

Now we're at the final step - getting some LLM's for Ollama to serve!  

<br/>

### Models
The Dockerfiles in this repository do not contain model downloads. Browse the [Ollama model library](https://ollama.com/library) and choose those that fit your needs and system capabilities.  

You can download models using a container's bash via `ollama pull <model-name:variant>`.

**The Ollama model directory for this repository's Dockerfiles is set to /myapp/LLM-Models**.  
 - If a directory is mounted to /myapp (`docker run -v <hostdirectory>:/myapp ...`), models will be stored in this directory, external to the images and containers.
 - If no directory is mounted to /myapp, the models will be stored in the images & containers.

<br/>

### Adding to your Docker image
The base setup is working! 🎉  
But now you need to change things so you can really experiment. In order to modify your Docker image to add a new library or save a model, it's only a few steps, and can be approached from two directions:
 - Run an Image, modify and then `commit` the Container as a new Image.
   -  Step 1: Start an interactive bash shell from the image, `docker run -it <imagename> /bin/bash`.
   -  Step 2: Make the changes you want to the container - install Python packages, edit environment variables, download models, etc.
   -  Step 3: Exit all shells. The container will stop.
   -  Step 4: Commit the changes made in the container to a new image: `docker commit <container-name> <new-image>`
   -  Any changes that were made have been preserved, and will be present on the next run of the `new-image`.
- Modify the Dockerfile and `build` a new Image
  -  Step 1: Open up the Dockerfile you want to start with in a text editor.
  -  Step 2: Make changes to the Dockerfile - add new lines with `RUN <command>` to install Python packages, edit environment variables, download models, etc. as the Image is built.
  -  Step 3: Save the changes to the Dockerfile.
  -  Step 4: Build the new Image from the Dockerfile.
```bash
#format
RUN <command>
#to install the Python library beautifulsoup4 as the final step of the Image build, you would add the following line to the bottom of the Dockerfile:
RUN pip install beautifulsoup4
```
