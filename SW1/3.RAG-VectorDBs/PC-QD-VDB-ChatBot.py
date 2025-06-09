import os
import numpy as np
from typing import List, Dict, Any, Optional
import openai
from sentence_transformers import SentenceTransformer
import pinecone
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

class VectorDBChatbot:
    def __init__(self, 
                 openai_api_key: str,
                 pinecone_api_key: str = None,
                 pinecone_environment: str = None,
                 qdrant_url: str = "http://localhost:6333",
                 use_pinecone: bool = True,
                 use_qdrant: bool = True):
        
        # Initialize OpenAI
        openai.api_key = openai_api_key
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize vector databases
        self.use_pinecone = use_pinecone
        self.use_qdrant = use_qdrant
        
        if self.use_pinecone and pinecone_api_key:
            self._init_pinecone(pinecone_api_key, pinecone_environment)
        
        if self.use_qdrant:
            self._init_qdrant(qdrant_url)
    
    def _init_pinecone(self, api_key: str, environment: str):
        """Initialize Pinecone vector database"""
        try:
            pinecone.init(api_key=api_key, environment=environment)
            
            # Create index if it doesn't exist
            index_name = "chatbot-knowledge"
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=self.embedding_dim,
                    metric='cosine'
                )
            
            self.pinecone_index = pinecone.Index(index_name)
            print("✅ Pinecone initialized successfully")
            
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {e}")
            self.use_pinecone = False
    
    def _init_qdrant(self, url: str):
        """Initialize Qdrant vector database"""
        try:
            self.qdrant_client = QdrantClient(url=url)
            
            # Create collection if it doesn't exist
            collection_name = "chatbot_knowledge"
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
            
            self.qdrant_collection = collection_name
            print("✅ Qdrant initialized successfully")
            
        except Exception as e:
            print(f"❌ Qdrant initialization failed: {e}")
            self.use_qdrant = False
    
    def add_knowledge(self, texts: List[str], metadata: List[Dict] = None):
        """Add knowledge to both vector databases"""
        if not texts:
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        if metadata is None:
            metadata = [{"text": text, "id": str(uuid.uuid4())} for text in texts]
        
        # Add to Pinecone
        if self.use_pinecone:
            try:
                vectors = []
                for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                    vectors.append({
                        "id": meta.get("id", str(uuid.uuid4())),
                        "values": embedding.tolist(),
                        "metadata": {"text": text, **meta}
                    })
                
                self.pinecone_index.upsert(vectors=vectors)
                print(f"✅ Added {len(vectors)} vectors to Pinecone")
                
            except Exception as e:
                print(f"❌ Pinecone upsert failed: {e}")
        
        # Add to Qdrant
        if self.use_qdrant:
            try:
                points = []
                for i, (text, embedding, meta) in enumerate(zip(texts, embeddings, metadata)):
                    points.append(PointStruct(
                        id=meta.get("id", str(uuid.uuid4())),
                        vector=embedding.tolist(),
                        payload={"text": text, **meta}
                    ))
                
                self.qdrant_client.upsert(
                    collection_name=self.qdrant_collection,
                    points=points
                )
                print(f"✅ Added {len(points)} points to Qdrant")
                
            except Exception as e:
                print(f"❌ Qdrant upsert failed: {e}")
    
    def search_knowledge(self, query: str, top_k: int = 3, db_type: str = "both") -> Dict[str, List]:
        """Search for relevant knowledge in vector databases"""
        query_embedding = self.embedding_model.encode([query])[0]
        results = {"pinecone": [], "qdrant": []}
        
        # Search Pinecone
        if self.use_pinecone and db_type in ["pinecone", "both"]:
            try:
                pinecone_results = self.pinecone_index.query(
                    vector=query_embedding.tolist(),
                    top_k=top_k,
                    include_metadata=True
                )
                
                for match in pinecone_results['matches']:
                    results["pinecone"].append({
                        "text": match['metadata']['text'],
                        "score": match['score'],
                        "metadata": match['metadata']
                    })
                    
            except Exception as e:
                print(f"❌ Pinecone search failed: {e}")
        
        # Search Qdrant
        if self.use_qdrant and db_type in ["qdrant", "both"]:
            try:
                qdrant_results = self.qdrant_client.search(
                    collection_name=self.qdrant_collection,
                    query_vector=query_embedding.tolist(),
                    limit=top_k
                )
                
                for result in qdrant_results:
                    results["qdrant"].append({
                        "text": result.payload['text'],
                        "score": result.score,
                        "metadata": result.payload
                    })
                    
            except Exception as e:
                print(f"❌ Qdrant search failed: {e}")
        
        return results
    
    def generate_response(self, query: str, db_type: str = "both") -> str:
        """Generate response using retrieved knowledge"""
        # Search for relevant knowledge
        search_results = self.search_knowledge(query, top_k=3, db_type=db_type)
        
        # Combine results from both databases
        all_contexts = []
        if search_results["pinecone"]:
            all_contexts.extend([r["text"] for r in search_results["pinecone"]])
        if search_results["qdrant"]:
            all_contexts.extend([r["text"] for r in search_results["qdrant"]])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_contexts = []
        for context in all_contexts:
            if context not in seen:
                seen.add(context)
                unique_contexts.append(context)
        
        # Create context for the prompt
        context = "\n\n".join(unique_contexts[:5]) if unique_contexts else "No relevant information found."
        
        # Generate response using OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""You are a helpful assistant. Use the following context to answer the user's question. If the context doesn't contain relevant information, say so and provide a general response.

Context:
{context}"""},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error generating the response: {e}"
    
    def compare_databases(self, query: str) -> Dict:
        """Compare search results between databases"""
        pinecone_results = self.search_knowledge(query, top_k=3, db_type="pinecone")
        qdrant_results = self.search_knowledge(query, top_k=3, db_type="qdrant")
        
        return {
            "query": query,
            "pinecone_results": pinecone_results["pinecone"],
            "qdrant_results": qdrant_results["qdrant"]
        }

# Example usage
def main():
    # Initialize chatbot (you'll need to provide your API keys)
    chatbot = VectorDBChatbot(
        openai_api_key="your-openai-key",
        pinecone_api_key="your-pinecone-key",
        pinecone_environment="your-pinecone-environment",
        qdrant_url="http://localhost:6333",  # Default Qdrant Docker URL
        use_pinecone=True,
        use_qdrant=True
    )
    
    # Add some sample knowledge
    sample_knowledge = [
        "Python is a high-level programming language known for its simplicity and readability.",
        "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
        "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently.",
        "Natural language processing (NLP) is a field of AI that focuses on the interaction between computers and human language.",
        "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data."
    ]
    
    metadata = [{"topic": "programming", "id": str(uuid.uuid4())} for _ in sample_knowledge]
    
    print("Adding knowledge to vector databases...")
    chatbot.add_knowledge(sample_knowledge, metadata)
    
    # Interactive chat loop
    print("\n🤖 Chatbot ready! Type 'quit' to exit, 'compare <query>' to compare databases.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower().startswith('compare '):
            query = user_input[8:]  # Remove 'compare ' prefix
            comparison = chatbot.compare_databases(query)
            
            print(f"\n🔍 Comparison for: '{query}'")
            print("\n📌 Pinecone Results:")
            for i, result in enumerate(comparison["pinecone_results"], 1):
                print(f"  {i}. Score: {result['score']:.3f} - {result['text'][:100]}...")
            
            print("\n🎯 Qdrant Results:")
            for i, result in enumerate(comparison["qdrant_results"], 1):
                print(f"  {i}. Score: {result['score']:.3f} - {result['text'][:100]}...")
        
        else:
            response = chatbot.generate_response(user_input)
            print(f"\n🤖 Bot: {response}")

if __name__ == "__main__":
    # Install required packages:
    # pip install openai sentence-transformers pinecone-client qdrant-client numpy
    
    # For Qdrant, you can run it locally with Docker:
    # docker run -p 6333:6333 qdrant/qdrant
    
    main()