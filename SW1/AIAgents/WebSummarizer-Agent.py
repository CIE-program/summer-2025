#Use Langchain workflow to create an AI Agent that scrapes, crawls, classifies and summarizes
#Credits: https://diamantai.substack.com/p/your-first-ai-agent-simpler-than
#By: Raghavendra Deshmukh, PESU CIE

from langgraph.graph import StateGraph
from langchain.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI 
from langchain.schema import HumanMessage
import os
from time import sleep
from typing import TypedDict, List
from dotenv import load_dotenv
# from duckduckgo_search import DDGS 

load_dotenv()

class State(TypedDict):
    text:str
    classification:str
    entities:List[str]
    summary:str
    url:str
    urls:List[str]
    information:str

llm = ChatMistralAI(model="mistral-small", temperature=0)

def web_scraper_node(state:State):
    '''Scrape the web to find a list of relevant urls'''
    
    prompt = PromptTemplate(
        input_variables=["text"],
        template="Search the web and return a list of comma separated relevant urls. \n\nTopic of Search:{text}\n\nUrls:"
    )

    message = HumanMessage(content=prompt.format(text=state["text"]))

    urls=llm.invoke([message]).content.strip().split(",")

    return {"urls":urls}

def web_crawler_node(state:State):
    '''Use the list of urls and obtain information from each of them'''

    prompt = PromptTemplate(
        input_variables=["urls"],
        template="From the given list of urls, search all of them, and assemble them into one unified detailed and exhaustive summary DO NOT reference the actual websites/urls, just provide a summary agnosic of the source.\n\nList of Urls:{urls}"
    )

    message = HumanMessage(content=prompt.format(urls=state["urls"]))

    information = llm.invoke([message]).content.strip()

    return {"information":information}


def classification_node(state:State):
    ''' Classify the given text into one of the categories: News, Blog, Research or Other '''

    prompt = PromptTemplate(
        input_variables=["information"],
        template="Classify the following text into one of the categories: News, Blog, Research, Article, Review or Other.\n\nInformation:{information}\n\nCategory:"
    )

    message = HumanMessage(content=prompt.format(information=state["information"]))

    classification = llm.invoke( [message] ).content.strip()

    return {"classification":classification}

def entity_extraction_node(state:State):
    ''' Extract all the entities (Person, Organization, Location) from the text'''

    prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract all the entities (Person, Organization, Location, Name, Place) from the following text. Provide the result as a comma-separated list.\n\nText:{text}\n\nEntities:"
    )

    message = HumanMessage(content=prompt.format(text=state["text"]))

    entities = llm.invoke([message]).content.strip().split(",")

    return {"entities":entities}

def summarization_node(state:State):
    ''' Summarize the text in one short sentence '''

    prompt = PromptTemplate(
        input_variables=["information"],
        template="Summarize the following text in one short sentence.\n\nInformation:{information}\n\nSummary:"
    )

    message = HumanMessage(content=prompt.format(information=state["information"]))

    summary = llm.invoke([message]).content.strip()

    return {"summary":summary}

workflow = StateGraph(State)

workflow.add_node("web_scraper_node",web_scraper_node)
sleep(2)
workflow.add_node("web_crawler",web_crawler_node)
sleep(2)
workflow.add_node("classification_node",classification_node)
sleep(2)
# workflow.add_node("extract_entity_node",entity_extraction_node)
workflow.add_node("summarization_node",summarization_node)
sleep(2)
workflow.set_entry_point("web_scraper_node")
sleep(2)
workflow.add_edge("web_scraper_node","web_crawler")
sleep(2)
workflow.add_edge("web_crawler","classification_node")
sleep(2)
# workflow.add_edge("classification_node","extract_entity_node")
workflow.add_edge("classification_node","summarization_node")
sleep(2)
app=workflow.compile()

sample_text = """
Give me a summary of the various pricing strategies for SaaS Products
"""
state_input = {"text": sample_text}
result = app.invoke(state_input)

print("Web search result:",result["urls"])
print("Web crawl result:",result["information"])
print("\nClassification:", result["classification"])
# print("\nEntities:", result["entities"])
print("\nSummary:", result["summary"])