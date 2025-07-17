### Using Tavily and creating an AI Agent with LlamaIndex Library
# Raghavendra Deshmukh, 17-Jul-2025
#Courtesy: Author, DeepSeek, Tavily, LlamaIndex Github
#https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/tools/llama-index-tools-tavily-research/examples/tavily.ipynb


from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.llms.mistralai import MistralAI
from llama_index.core.agent import FunctionCallingAgent
from llama_index.agent.openai import OpenAIAgent
from time import sleep
import os

# Load API keys
mistral_key = os.environ["MISTRAL_API_KEY"]
tavily_key = os.environ["TAVILY_API_KEY"]

# Set up Mistral LLM.  If you do not have Mistral, please use your respective LLM and add the appropriate Import statements
llm = MistralAI(
    model="mistral-large-latest",
    api_key=mistral_key,
)

tavily_tool = TavilyToolSpec(
    api_key=tavily_key,
)

tavily_tool_list = tavily_tool.to_tool_list()
for tool in tavily_tool_list:
    print(tool.metadata.name)
print(tavily_tool.search("Who won the England-India 3rd Test match? Give me short crisp details and not long answers", max_results=3))

agent = FunctionCallingAgent.from_tools(
    tavily_tool_list,
    llm=llm,
)
sleep(2)

print(
    agent.chat(
        "Write a deep analysis in markdown syntax about the latest England-India Test match"
    )
)

#### The below code runs only with OpenAI Key.  The OpenAI Agent from LLamaIndex expects the OpenAI Key
#sleep(2)
#print("********\n\n")
#openAIAgent = OpenAIAgent.from_tools(tavily_tool_list)
#print(openAIAgent.chat('Write a deep analysis in markdown syntax about the latest England-India Test match'))