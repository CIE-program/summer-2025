import os
from dotenv import load_dotenv
import json
import pickle
from typing import List, Dict, Any, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# Core libraries
import numpy as np
import faiss
from PIL import Image
import fitz  # PyMuPDF
import base64
from io import BytesIO

# HuggingFace
from transformers import AutoTokenizer, AutoModel, BlipProcessor, BlipForConditionalGeneration
from sentence_transformers import SentenceTransformer
import torch

# Mistral AI
from mistralai.client import MistralClient
from mistralai import Mistral

load_dotenv()

class PDFMultimodalProcessor:
    def __init__(self, mistral_api_key: str, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the PDF processor with multimodal capabilities
        
        Args:
            mistral_api_key: Mistral AI API key
            embedding_model: HuggingFace embedding model name
        """
        self.mistral_client = Mistral(api_key=mistral_api_key)
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize image captioning model
        print("Loading image captioning model...")
        self.image_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.image_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # FAISS index
        self.index = None
        self.documents = []
        self.metadata = []
        
        print("✅ PDF Multimodal Processor initialized successfully!")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text content from PDF pages"""
        doc = fitz.open(pdf_path)
        text_content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():  # Only add non-empty text
                text_content.append({
                    'content': text.strip(),
                    'type': 'text',
                    'page': page_num + 1,
                    'source': pdf_path
                })
        
        doc.close()
        return text_content
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract images from PDF and generate captions"""
        print("*** Extract Images from PDF ***")
        doc = fitz.open(pdf_path)
        image_content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Extract image
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        img_pil = Image.open(BytesIO(img_data))
                        
                        # Generate caption using BLIP
                        caption = self.generate_image_caption(img_pil)
                        
                        # Create detailed description using Mistral
                        detailed_desc = self.analyze_image_with_mistral(img_pil, caption)
                        
                        image_content.append({
                            'content': f"Image Caption: {caption}\nDetailed Analysis: {detailed_desc}",
                            'type': 'image',
                            'page': page_num + 1,
                            'source': pdf_path,
                            'image_index': img_index,
                            'caption': caption,
                            'detailed_description': detailed_desc
                        })
                    
                    pix = None
                except Exception as e:
                    print(f"Error processing image on page {page_num + 1}: {str(e)}")
                    continue
        
        doc.close()
        return image_content
    
    def generate_image_caption(self, image: Image.Image) -> str:
        """Generate caption for an image using BLIP"""
        print("***Generate Image Captions ***")
        try:
            # Resize image if too large
            if image.size[0] > 512 or image.size[1] > 512:
                image.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            inputs = self.image_processor(image, return_tensors="pt")
            
            with torch.no_grad():
                out = self.image_model.generate(**inputs, max_length=50, num_beams=5)
            
            caption = self.image_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            return f"Image analysis failed: {str(e)}"
    
    def analyze_image_with_mistral(self, image: Image.Image, caption: str) -> str:
        """Get detailed analysis of image using Mistral AI"""
        try:
            # Convert image to base64 for API
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt = f"""
            I have an image with this initial caption: "{caption}"
            
            Please provide a detailed analysis of this image considering it might be from:
            - A presentation slide or pitch deck
            - University class notes or educational material
            - A diagram, chart, or infographic
            
            Focus on:
            1. What information or data is being presented
            2. Any text visible in the image
            3. The purpose or context of this visual element
            4. Key takeaways or insights
            
            Keep the analysis concise but informative (2-3 sentences).
            """
            
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[
                {
                    "role": "user",
                    "content": prompt
                }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Detailed analysis unavailable: {str(e)}"
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Process a PDF to extract both text and images"""
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text content
        print("- Extracting text...")
        text_content = self.extract_text_from_pdf(pdf_path)
        print(f"  Found {len(text_content)} text sections")
        
        # Extract and analyze images
        print("- Extracting and analyzing images...")
        image_content = self.extract_images_from_pdf(pdf_path)
        print(f"  Found {len(image_content)} images")
        
        # Combine all content
        all_content = text_content + image_content
        print(f"✅ Total content pieces: {len(all_content)}")
        
        return all_content
    
    def create_embeddings(self, content_list: List[Dict]) -> np.ndarray:
        """Create embeddings for all content"""
        print("Creating embeddings...")
        texts = [item['content'] for item in content_list]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings.astype('float32')
    
    def build_vector_database(self, content_list: List[Dict]):
        """Build FAISS vector database"""
        if not content_list:
            print("No content to process!")
            return
        
        print("Building vector database...")
        
        # Create embeddings
        embeddings = self.create_embeddings(content_list)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents = [item['content'] for item in content_list]
        self.metadata = content_list
        
        print(f"✅ Vector database built with {len(self.documents)} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search the vector database"""
        if self.index is None:
            print("Vector database not built yet!")
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query]).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx != -1:  # Valid result
                result = {
                    'rank': i + 1,
                    'score': float(score),
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx]
                }
                results.append(result)
        
        return results
    
    def ask_question(self, question: str, top_k: int = 3) -> str:
        """Ask a question and get AI-generated answer based on retrieved content"""
        # Search for relevant content
        search_results = self.search(question, top_k)
        
        if not search_results:
            return "No relevant content found in the database."
        
        # Prepare context from search results
        context_parts = []
        for result in search_results:
            content_type = result['metadata']['type']
            page = result['metadata']['page']
            source = Path(result['metadata']['source']).name
            
            context_parts.append(
                f"[{content_type.upper()} - Page {page} from {source}]\n{result['content']}"
            )
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using Mistral
        prompt = f"""
        Based on the following content from PDF documents, please answer the question.
        
        CONTEXT:
        {context}
        
        QUESTION: {question}
        
        Please provide a comprehensive answer based on the context provided. If the context contains both text and image information, make sure to incorporate insights from both types of content. Clearly indicate when you're referencing visual elements vs text content.
        """
        
        try:
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def save_database(self, save_path: str):
        """Save the vector database and metadata"""
        if self.index is None:
            print("No database to save!")
            return
        
        save_dir = Path(save_path)
        save_dir.mkdir(exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_dir / "faiss_index.bin"))
        
        # Save metadata and documents
        with open(save_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        
        with open(save_dir / "documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"✅ Database saved to {save_path}")
    
    def load_database(self, load_path: str):
        """Load a saved vector database"""
        load_dir = Path(load_path)
        
        if not load_dir.exists():
            print(f"Database path {load_path} does not exist!")
            return
        
        # Load FAISS index
        self.index = faiss.read_index(str(load_dir / "faiss_index.bin"))
        
        # Load metadata and documents
        with open(load_dir / "metadata.json", 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        with open(load_dir / "documents.pkl", 'rb') as f:
            self.documents = pickle.load(f)
        
        print(f"✅ Database loaded from {load_path}")
        print(f"   Total documents: {len(self.documents)}")

    def display_query_results(self, results: List[Dict], show_images: bool = False):
        """Display query results in a formatted way"""
        if not results:
            print("No results found!")
            return
        
        print(f"\n📋 Found {len(results)} results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            content_type = metadata['type']
            page = metadata['page']
            source = metadata['source'].split('/')[-1]  # Just filename
            score = result['score']
            
            print(f"\n🔍 Result {i} - {content_type.upper()}")
            print(f"📄 Source: {source} (Page {page})")
            print(f"📊 Similarity Score: {score:.4f}")
            
            if content_type == 'image':
                print(f"🖼️ Image Caption: {metadata.get('caption', 'N/A')}")
                print(f"📝 Description: {metadata.get('detailed_description', 'N/A')}")
                
                if show_images:
                    self._display_stored_image(metadata, source, page)
            else:
                # Text content
                content = result['content']
                if len(content) > 200:
                    print(f"📄 Content: {content[:200]}...")
                else:
                    print(f"📄 Content: {content}")
            
            print("-" * 60)

    #This function will be called upon to query the images in the Vector DB based on the Keywords
    #It will use the search function of this class to find the images and return the top K that is requested
    def query_images_only(self, query: str, top_k: int = 3) -> List[Dict]:
        """Query specifically for images from the vector database"""
        if self.index is None:
            print("Vector database not built yet!")
            return []
        
        # Get all results first
        all_results = self.search(query, top_k=top_k*3)  # Get more to filter
        
        # Filter for image content only
        image_results = [r for r in all_results if r['metadata']['type'] == 'image']
        
        return image_results[:top_k]        

    #This function will allow us to find images by using a keyword
    def find_images_by_keyword(self, keyword: str, top_k: int = 5) -> List[Dict]:
        """Find images that contain specific keywords in their captions or descriptions"""
        print(f"🔍 Searching for images containing: '{keyword}'")
        
        image_results = self.query_images_only(keyword, top_k=top_k)
        
        if image_results:
            print(f"Found {len(image_results)} relevant images:")
            self.display_query_results(image_results, show_images=True)
        else:
            print("No images found matching your keyword.")
        
        return image_results


# Usage Example
def main():
    # Initialize the processor
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    
    print("Setting up the Processor Object using the Mistral AI API Key and Embedding Model")
    processor = PDFMultimodalProcessor(
        mistral_api_key=MISTRAL_API_KEY,
        embedding_model="all-MiniLM-L6-v2"  # You can use other models like "all-mpnet-base-v2"
    )
    
    # Process multiple PDFs
    #pdf_files = [
    #    "RAGMaterial1.pdf",
    #    "RAGMaterial2.pdf",
    #    "RAGMaterial3.pdf"
    #]
    
    pdf_files = ["PM101.pdf"]

    print("Processing the 3 PDF Files that are hardcoded for Reading")
    all_content = []
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            content = processor.process_pdf(pdf_file)
            all_content.extend(content)
        else:
            print(f"⚠️ File not found: {pdf_file}")
    
    if all_content:
        print("Building the Vector DB using the Content of the PDF that has been read - build_vector_database()")
        # Build vector database
        processor.build_vector_database(all_content)
        
        print("Saving the Vector DB - save_database()")
        # Save the database
        processor.save_database("./pdf_multimodal_db")
        
        # Example searches
        print("\n" + "="*50)
        print("SEARCH EXAMPLES")
        print("="*50)
        
        # Text-based search
        results = processor.search("What is RAG", top_k=3)
        print(f"\nSearch Results for 'What is RAG':")
        for result in results:
            print(f"- [{result['metadata']['type']}] Page {result['metadata']['page']}: {result['content'][:100]}...")
        
        # Ask questions
        print(f"\nQ&A Examples:")
        
        questions = [
            "History of Product Management"
            #"How is RAG related to AI?",
            #"Explain the Steps in RAG in a few sentences",
            #"What are the frameworks for RAG?"
        ]
        
        for question in questions:
            print(f"\nQ: {question}")
            answer = processor.ask_question(question)
            print(f"A: {answer}")
    
    else:
        print("No content processed. Please check your PDF files.")

    #Now query for Text
    image_results = processor.find_images_by_keyword("History of Product Management", top_k=5)
    print("*** Keyword to search for Images is: History of Product Management")
    print(f"*** The retrieved Images are here: {image_results}")


#Let us Start here to process PDFs with Text and Images
if __name__ == "__main__":
    print("** START MAIN ***")
    main()