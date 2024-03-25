#start_chainlit_general_chatbot.py

#   This file is for starting the chainlit general chatbot via the 'python' command.
#   This script requires the following packages to be installed: subprocess

import subprocess

# Start the script using 'chainlit run'
process = subprocess.run(["chainlit", "run", "/myapp/LangChain_Projects/scripts/chainlit_general_chatbot.py"])