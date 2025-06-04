#By: Raghavendra Deshmukh. PESU CIE - Industry Mentor
#Date: May 2025
#Purpose: Teaching Langchain based RAG Chat system as part of 2025 Summer Courses
#Credits: Langchain Documentation, Author's Code

#This is a simple RAG Example using Langchain as a Library.
#We will use all of the LangChain's libraries which as on today's date (27th May 2025) is listed at v0.3 to build the initial 
#experiments on RAG.

#Langchain will now be referred in the comments as LC

#The idea here is to introduce the steps involved in RAG
#1. Load PDF Documents (It can also be Webpages, Text files, CSVs etc) using a PDF Loader called PyPDFLoader that we use from LC
#2. Split or Chunk the Documents using a RecursiveCharacterTextSplitter (there are other splitters as well)
    #--> https://python.langchain.com/api_reference/text_splitters/index.html for latex, markdown, nltk, spacy, sentence transformers
#3. Create an Embeddings to represent the Chunks of the Documents as a specific math or numeric representation called Vectors
    #--> Embeddings are provided by a variety of providers including LLM providers like OpenAI, Mistral, Ollama etc 
    #--> https://python.langchain.com/docs/integrations/text_embedding/
#4. Use a Vector Database/DataStore to store the Document Chunks and the Vectors.
    #--> Popular Vector DBs include ChromaDB, FAISS, QDrant, Pinecone, MongoDB and many more. 
    #--> https://python.langchain.com/docs/integrations/vectorstores/
#5. We then Search for a specific Query on the Document using the Vector DB
    #--> There are many methods of Searching like Similarity, Similarity With Score etc
#6. We then Search using Retrievers with different Search types - Similarity, MMR, similarity_score_threshold
    #-->https://python.langchain.com/api_reference/core/vectorstores/langchain_core.vectorstores.base.VectorStoreRetriever.html#langchain_core.vectorstores.base.VectorStoreRetriever

#Note: FAISS means Facebook AI Similarity Search

#Install the following before running this code:
#pip install --upgrade langchain-text-splitters langchain-community langgraph
#pip install -qU "langchain[mistralai]" #We do not need this for this code but when we use an LLM for retrieval
#pip install -qU langchain-huggingface

#Based on what Vector DB we use, we need one of the 2 below.  For the moment we will use FAISS so we use the langchain-community
#pip install -qU langchain-community
#We shall use this only if we use QDrant as our Vector DB
#pip install -qU langchain-qdrant

import os
from dotenv import load_dotenv
#from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import chain


load_dotenv()

LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
PDF_PATH=r"E:\Deshmukh2025\PESU-CIE\Projects\AI\RAG\pdfs\AI-PM1.pdf"
FAISS_INDEX_PATH = "faiss_index"  # Directory to save FAISS index

#Load the PDFs
loader = PyPDFLoader(PDF_PATH)
docs=loader.load()
print(f"The Length of the Documents is: {len(docs)}")
print(f"{docs[0].page_content[:200]}\n")
print(docs[0].metadata)

#Use the CharacterTextSplitter and get the Splits of the Sentences from the PDF
#Create an overlap of 200 characters for each chunk that is created which is of 1000
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
print(len(all_splits))

#Initialize the Mistral AI LLM
#llm = init_chat_model("mistral-large-latest", model_provider="mistralai")

#Use the HuggingFace Embeddings - If you need to use any other Embeddings of a particular LLM you would need an API Key
#On first time load, the model will be downloaded on the local machine and will take time
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)

assert len(vector_1) == len(vector_2)
print(f"Generated vectors of length {len(vector_1)}\n")
print(vector_1[:10])

#Initialize the Vector DB - I am using FAISS.  But there are options for QDrant, ChromaDB, InMemory etc.
vector_store = FAISS.from_documents(all_splits, embeddings)
print("FAISS Vector Store is created")
#We will now index the documents
#ids = vector_store.add_documents(documents=all_splits)


print("*** Using Similarity Search ***")
#Use the Vector Store/DB and use a Similarity Search to get information from the Vector DB
results = vector_store.similarity_search(
    "What is the impact of AI in Product Management"
)
print(results[0])

print("*** Using Similarity Search with Score ***")
results = vector_store.similarity_search_with_score("What is the impact of AI in Product Management")
doc, score = results[0]
print(f"Score: {score}\n")
print(doc)

print("*** Return the Embedding Documents that were retrieved for the Query")
embedding = embeddings.embed_query("What is the impact of AI in Product Management")
results = vector_store.similarity_search_by_vector(embedding)
print(results[0])

print("\n\n*** Retrievers - Using vector store as a Retriever ***")
query = "What are the responsibilities of an AI Product Manager"
similarity_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2},
)
similarity_results = similarity_retriever.get_relevant_documents(query)
print("\n=== SIMILARITY SEARCH RESULTS ===")
for i, doc in enumerate(similarity_results):
    print(f"--- Chunk {i+1} ---")
    print(doc.page_content[:500])  # Show first 300 characters
    print()

mmr_retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 2},
)
mmr_results = mmr_retriever.get_relevant_documents(query)
print("\n=== MMR SEARCH RESULTS ===")
for i, doc in enumerate(mmr_results):
    print(f"--- Chunk {i+1} ---")
    print(doc.page_content[:500])
    print()

#retriever2.batch(
# [
#        "What are the various branches of AI discussed in the Paper?",
#        "What are the responsibilities of an AI Product Manager",
#    ],
#)
# VectorStoreRetriever supports search types of "similarity" (default), "mmr" (maximum marginal relevance), 
# and "similarity_score_threshold".  We can use the latter to threshold documents output by the retriever by similarity score.
##
#print("\n*** Retrievers - Using vector store similarity search ***")
#@chain
#def retriever1(query: str) -> List[Document]:
#    return vector_store.similarity_search(query, k=2)
#print(retriever1.batch(
#    [
#        "What are the various branches of AI discussed in the Paper?",
#        "What are the responsibilities of an AI Product Manager",
#    ],
#))


