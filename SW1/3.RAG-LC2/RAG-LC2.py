#By: Raghavendra Deshmukh. PESU CIE - Industry Mentor
#Date: May 2025
#Purpose: Teaching Langchain based RAG Chat system as part of 2025 Summer Courses
#Credits: Langchain Documentation, Author's Code, Claude AI and some imagination

#This program extends the Basic RAG system to use an LLM - Mistral AI to create a Chat Bot
    #-->It uses FAISS Vector DB in a specific distance strategy for search of Strings called Cosine which is better suited for 
    #-->Text Search purposes
#This program modularizes the Basic RAG program via separating the unique activities in functions. 

#1. Adds a RAG Testing function
#2. Provides options to show the Sources being used in this system
#3. Calculates the Time taken to respond to a question
#4. Offers an interactive way to chat with the uploaded PDF 

import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from typing import List
import time

load_dotenv()

# Environment variables
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
PDF_PATH = r"E:\Deshmukh2025\PESU-CIE\Projects\AI\RAG\pdfs\AI-PM1.pdf"
FAISS_INDEX_PATH = "faiss_index"

def load_and_process_pdf():
    """Load and process the PDF document"""
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    print(f"The Length of the Documents is: {len(docs)}")
    #print(f"{docs[0].page_content[:200]}\n")
    #print(f"Metadata: {docs[0].metadata}")
    
    return docs

def create_text_splits(docs):
    """Create text splits from documents"""
    print("Creating text splits...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    print(f"Created {len(all_splits)} text chunks")
    return all_splits

def setup_vector_store(all_splits):
    """Set up the vector store with embeddings"""
    print("Setting up embeddings and vector store...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    
    # Create vector store
    vector_store = FAISS.from_documents(all_splits, embeddings, distance_strategy="COSINE")
    print("FAISS Vector Store created successfully")
    
    # Save the vector store for future use
    try:
        vector_store.save_local(FAISS_INDEX_PATH)
        print(f"Vector store saved to {FAISS_INDEX_PATH}")
    except Exception as e:
        print(f"Could not save vector store: {e}")
    
    return vector_store, embeddings

def load_existing_vector_store():
    """Load existing vector store if available"""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True, distance_strategy="COSINE")
        print("Loaded existing vector store")
        return vector_store, embeddings
    except Exception as e:
        print(f"Could not load existing vector store: {e}")
        return None, None

def setup_mistral_llm():
    """Initialize Mistral AI LLM"""
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY not found in environment variables")
    
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=MISTRAL_API_KEY,
        temperature=0.3
    )
    print("Mistral AI LLM initialized")
    return llm

def create_rag_chain(vector_store, llm):
    """Create the RAG chain for question answering"""
    
    # Create retriever
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 8}
    )
    
    # Create prompt template
    #The {context} and {question} are NOT Python f-string variables. They are LC template placeholders that work 
    # differently compared to Python String Substitutions.
    # They are parsed and substituted during the invocation phase in the code snippets below when the rag_chain object is created.
    #  
    prompt_template = ChatPromptTemplate.from_template("""
    You are an AI assistant that answers questions based on the provided context from a PDF document about AI and Product Management.
    
    Context: {context}
    
    Question: {question}
    
    Instructions:
    - Answer the question based primarily on the provided context
    - If the context doesn't contain enough information, say so clearly
    - Provide specific details and examples from the context when available
    - Keep your answer comprehensive but concise
    - If you reference specific information, try to indicate which part of the document it comes from
    
    Answer:
    """)
    
    def format_docs(docs):
        """Format retrieved documents for context"""
        formatted = []
        for i, doc in enumerate(docs):
            page_info = f"Page {doc.metadata.get('page', 'unknown')}" if doc.metadata else "Source unknown"
            formatted.append(f"[{page_info}]: {doc.page_content}")
        return "\n\n".join(formatted)
    
    # Create the RAG chain
    #Here we use the LC's Chain Composition to send the output of one step as an input to the next step separated by | - Pipe Operator
    #More details will be in the README
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, retriever

def chat_with_pdf(rag_chain, retriever):
    """Interactive chat function"""
    print("\n" + "="*60)
    print("🤖 AI PDF Chat Assistant")
    print("="*60)
    print("You can now ask questions about your PDF!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'help' for available commands.")
    print("-"*60)
    
    while True:
        try:
            question = input("\n💬 Your question: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for using the AI PDF Chat Assistant!")
                break
                
            if question.lower() == 'help':
                print("\n📋 Available commands:")
                print("  • Ask any question about the PDF content")
                print("  • 'quit', 'exit', 'bye' - End conversation")
                print("  • 'help' - Show this help message")
                print("  • 'sources' - Show sources for last question")
                continue
                
            if question.lower() == 'sources':
                print("\n📚 Retrieving relevant sources...")
                try:
                    docs = retriever.get_relevant_documents(question)
                    for i, doc in enumerate(docs, 1):
                        page_info = f"Page {doc.metadata.get('page', 'unknown')}"
                        print(f"\n--- Source {i} ({page_info}) ---")
                        print(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                except Exception as e:
                    print(f"Error retrieving sources: {e}")
                continue
            
            print("\n🤔 Thinking...")
            start_time = time.time()
            
            # Get answer from RAG chain
            answer = rag_chain.invoke(question)
            
            response_time = time.time() - start_time
            
            print(f"\n🤖 Answer (responded in {response_time:.2f}s):")
            print("-" * 50)
            print(answer)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Conversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.")

def main():
    """Main function to run the RAG system"""
    try:
        # Try to load existing vector store first
        vector_store, embeddings = load_existing_vector_store()
        
        if vector_store is None:
            # If no existing vector store, create new one
            docs = load_and_process_pdf()
            all_splits = create_text_splits(docs)
            vector_store, embeddings = setup_vector_store(all_splits)
        
        # Initialize Mistral LLM
        llm = setup_mistral_llm()
        
        # Create RAG chain
        rag_chain, retriever = create_rag_chain(vector_store, llm)
        
        print("\n✅ System ready!")
        
        # Test with some example questions
        print("\n" + "="*60)
        print("🧪 TESTING THE SYSTEM")
        print("="*60)
        
        test_questions = [
            "What is the impact of AI in Product Management?",
            "What are the responsibilities of an AI Product Manager?",
            "How does AI transform product development processes?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Test Question {i}: {question}")
            print("-" * 50)
            try:
                answer = rag_chain.invoke(question)
                print(f"🤖 Answer: {answer[:300]}..." if len(answer) > 300 else f"🤖 Answer: {answer}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Start interactive chat
        chat_with_pdf(rag_chain, retriever)
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        print("Please check your environment variables and file paths.")

if __name__ == "__main__":
    main()