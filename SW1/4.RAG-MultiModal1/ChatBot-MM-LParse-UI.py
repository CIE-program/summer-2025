import nest_asyncio
import os
import faiss
import numpy as np
from llama_parse import LlamaParse
from llama_index.core.schema import TextNode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import BlipProcessor, BlipForConditionalGeneration
from llama_index.llms.mistralai import MistralAI
from PIL import Image
import torch
from dotenv import load_dotenv
import pickle
import streamlit as st

nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Constants
FAISS_INDEX_FILE = "faiss_index.index"
NODES_DATA_FILE = "nodes_data.pkl"
IMAGE_METADATA_FILE = "processed_images.pkl"

# Initialize components
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
parser = LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"), result_type="markdown")
llm = MistralAI(api_key=os.getenv("MISTRAL_API_KEY"), model="mistral-small")  # For generation

# Initialize BLIP model for image captioning
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_alt_text(image_path):
    """Generate alt text for an image using BLIP model"""
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        caption = blip_model.generate(**inputs)
    return blip_processor.decode(caption[0], skip_special_tokens=True)

def load_processed_images():
    """Load set of already processed images"""
    if os.path.exists(IMAGE_METADATA_FILE):
        with open(IMAGE_METADATA_FILE, "rb") as f:
            return pickle.load(f)
    return set()

def save_processed_images(processed_images):
    """Save set of processed images"""
    with open(IMAGE_METADATA_FILE, "wb") as f:
        pickle.dump(processed_images, f)

def process_new_images(json_objs, processed_images):
    """Process only new images in the PDF"""
    print("Proces New Image")
    image_dicts = parser.get_images(json_objs, download_path="llamaimages")
    new_nodes = []
    
    for image_dict in image_dicts:
        image_path = image_dict["path"]
        if image_path not in processed_images:
            alt_text = generate_alt_text(image_path)
            new_nodes.append(TextNode(text=alt_text, metadata={"path": image_path}))
            processed_images.add(image_path)
    
    save_processed_images(processed_images)
    return new_nodes

def load_or_create_index(pdf_path):
    """Load existing index or create new one if needed"""
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(NODES_DATA_FILE):
        print("Loading existing FAISS index...")
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(NODES_DATA_FILE, "rb") as f:
            nodes = pickle.load(f)
        return index, nodes
    
    print("Creating new FAISS index...")
    # Parse PDF and process content
    json_objs = parser.get_json_result(pdf_path)
    json_list = json_objs[0]["pages"]
    
    # Process text nodes
    text_nodes = [TextNode(text=page["text"], metadata={"page": page["page"]}) 
                 for page in json_list]
    
    # Process only new images
    processed_images = load_processed_images()
    image_nodes = process_new_images(json_objs, processed_images)
    
    # This is where we merge the Text and Image Nodes
    print("Now merging the Text and Image Nodes")
    nodes = text_nodes + image_nodes
    
    # Create FAISS index
    embeddings = [embed_model.get_text_embedding(node.text) for node in nodes]
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    # Save index and nodes
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(NODES_DATA_FILE, "wb") as f:
        pickle.dump(nodes, f)
    
    return index, nodes

def query_index(index, nodes, query, k=3):
    """Query the FAISS index"""
    query_embedding = embed_model.get_text_embedding(query)
    distances, indices = index.search(np.array([query_embedding]).astype('float32'), k)
    return [nodes[i] for i in indices[0]]

def generate_response(query, context_nodes):
    """Generate LLM response using retrieved context"""
    # Combine all context into a single string
    context = "\n\n".join([f"Source {i+1} (from {node.metadata}):\n{node.text}" 
                          for i, node in enumerate(context_nodes)])
    
    # Create prompt with context
    prompt = f"""You are an expert assistant analyzing documents with text and images.
    Answer the question using only the provided context. If you do not know, say so.
    
    Context:
    {context}

    Question: {query}
    Answer: """
    
    # Get LLM response
    response = llm.complete(prompt)
    return response.text

# Main execution flow
if __name__ == "__main__":
    st.title("Multimodal PDF Chatbot - powered by Llamaparse🦙")

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        # Save uploaded file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(pdf_file.getbuffer())

    if st.button("Process PDF"):
        with st.spinner(f"Extracting and Processing {pdf_file} ..."):            
            # Step 1: Load or create index
            index, nodes = load_or_create_index("temp.pdf")
            st.session_state['index'] = index
            st.session_state['nodes'] = nodes
            st.success("Processing complete ...")

    if 'index' in st.session_state:    
        # Step 2: Query the index
        question = st.text_input("🤖Hi!! there, Ask me a question about your document: ")
        if question:
            with st.spinner("🕵🏻Searching... Hang in there... "):
                results_context = query_index(st.session_state['index'], st.session_state['nodes'], question, k=8)
    

                # Use an LLM to Generate a Response for the Question asked
                response = generate_response(question, results_context)
                st.caption(f"❓Your Question: {question}")
                st.markdown(f"👉{response}")    
            
                # Display results directly retrieved from the Vector DB
                with st.expander("📃View supporting content ..."):
                    for i, result in enumerate(results_context, 1):
                        print(result.metadata)
                        col1, col2 = st.columns([1,3])
                        if 'path' in result.metadata:
                            print("Image and Text")
                            with col1:    
                                st.image(result.metadata["path"], width=150)
                            with col2:    
                                st.caption("Image details: ")
                                st.write(result.text)
                        else:
                            st.write(f"**Page {result.metadata.get('page', '?')}:**")
                            st.write(result.text)    
                        st.divider()
