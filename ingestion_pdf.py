import warnings
warnings.filterwarnings("ignore")
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
import tempfile
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

""" 
Ingests data/document.pdf into 'yourdocs' chroma collection.
Applies RecursiveCharacterTextSplitter to chunk the document.
Run once (or after regenrating the PDF) : python ingestion.py
"""
CHROMA_DIR = "chroma_store"
COLLECTION = "yourdocs"
PDF_PATH = os.path.join("data", "document.pdf")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

def ingest_pdf(uploaded_file):
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
            separator = ["\n\n","\n","."," "],
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP,
        )
        chunks  = text_splitter.split_documents(pages)
        print(f"Created {len(chunks)} chunks.")

        print("Creating embedding model...")
        embeddings = HuggingFaceEmbeddings(model_name = EMBED_MODEL)

        print("Embedding and Storing in Chroma collection '{COLLECTION}'...")
        vector_store = Chroma.from_documents(
            documents= chunks,
            embedding = embeddings,
            collection_name = COLLECTION,
            persist_directory = CHROMA_DIR,
        )

        return f"Done. {vector_store._collection.count()} vectors stored."

    finally:
        os.unlink(temp_pdf_path)
