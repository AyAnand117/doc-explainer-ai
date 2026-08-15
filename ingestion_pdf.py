import warnings
warnings.filterwarnings("ignore")
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
import tempfile
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

""" 
Processes a user-uploaded PDF and stores it in a unique Chroma vector collection.

The pipeline:
1. Saves the uploaded PDF to a temporary file.
2. Extracts text using PyPDFLoader.
3. Splits the document into overlapping chunks.
4. Generates embeddings using HuggingFaceEmbeddings.
5. Stores the embeddings in a uniquely named Chroma collection.

Returns :
    str : The Chroma collection name for the uploaded document.
    None: If ingestion fails. 
"""

CHROMA_DIR = "chroma_store"
#COLLECTION = "yourdocs"
#PDF_PATH = os.path.join("data", "document.pdf")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100



def ingest_pdf(uploaded_file):

    collection_name = f"doc_{uuid.uuid4().hex}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        temp_pdf_path = tmp_file.name

    try:
        print("Loading PDF...")
        loader = PyPDFLoader(temp_pdf_path)
        pages = loader.load()
        print(f"{len(pages)} pages loaded")


        print("Chunking document...")
        text_splitter =RecursiveCharacterTextSplitter(
            separators = ["\n\n","\n","."," "],
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP,
        )
        chunks  = text_splitter.split_documents(pages)
        print(f"Created {len(chunks)} chunks.")

        print("Creating embedding model...")
        embeddings = HuggingFaceEmbeddings(model_name = EMBED_MODEL)

        print("Embedding and Storing in Chroma collection '{collection_name}'...")
        vector_store = Chroma.from_documents(
            documents= chunks,
            embedding = embeddings,
            collection_name = collection_name,
            persist_directory = CHROMA_DIR,
        )

        print(f"Done. {vector_store._collection.count()} vectors stored.")
        
        return collection_name

    finally:
        os.unlink(temp_pdf_path)
