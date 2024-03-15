#  This script is an extremely simple example of a basic invoke of an LLM using LangChain & served by Ollama (paraphrased from the LangChain QuickStart docs @ https://python.langchain.com/docs/get_started/quickstart)
#  This script requires the following to be installed: langchain, ollama, 

#Make sure the Ollama server is running. After that, you can do:
import langchain
from langchain_community.llms import Ollama
mistral_instruct = Ollama(model="mistral:instruct")

#Once you've installed and initialized the LLM of your choice, we can try using it! 
#   Let's ask it what LangSmith is - this is something that wasn't present in the training data 
#   so it shouldn't have a very good response.
#mistral_instruct.invoke({"input": "how can langsmith help with testing?"})

#We can also guide it's response with a prompt template. 
#   Prompt templates are used to convert raw user input to a better input to the LLM.
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a world class technical documentation writer."),
    ("user", "{input}")
])

#The output of a ChatModel (and therefore, of most chains) is a message. 
#   However, it's often much more convenient to work with strings. 
#   Let's add a simple output parser to convert the chat message to a string.
from langchain_core.output_parsers import StrOutputParser
output_parser = StrOutputParser()

#We can now add this to the previous chain:
chain = prompt | mistral_instruct | output_parser

#We can now invoke it and ask the same question. 
#   The answer will now be a much more printable string (rather than a ChatMessage).
print(chain.invoke({"input": "how can langsmith help with testing?"}))
