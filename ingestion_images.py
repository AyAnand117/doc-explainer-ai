import os
from pathlib import Path
import tempfile
import uuid

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from PIL import Image
import pytesseract # OCR tool


from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma



""" 
Processes a user-uploaded image and stores its extracted text in a unique Chroma vector collection.

The pipeline:
1. Saves the uploaded image to a temporary file.
2. Extracts the text using OCR (Tesseract).
3. Converts the extracted text into a Langchain document. 
4. Splits the text into overlapping chunks.
5. Generates embedding for each chunk. 
6. Stores chunks and embeddings in a unique Chroma collection.

Returns :
    str : The Chroma collection name for the uploaded image.
"""

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
CHROMA_DIR = "chroma_store"
#COLLECTION = "yourdocs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

def ingest_image(uploaded_file):
    """
    Extracts text from an uploaded image using OCR, then chunks it,
    embeds it, and stores it in Chroma.
    """
    collection_name = f"img_{uuid.uuid4().hex}"

    file_suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(delete=False, suffix =file_suffix) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        temp_file_path = tmp_file.name

    try :
        print("Extracting text from image using OCR...")
        image = Image.open(temp_file_path)
        extracted_text = pytesseract.image_to_string(image)
        if not extracted_text.strip():
            raise ValueError("OCR extracted no text - image may not contain text or OCR failed")
        else:
            print("OCR complete. Extracted text : ")
            print(extracted_text[:100])
        
        # Conversion to langchain document
        document = Document(
            page_content = extracted_text,
            metadata = {"source":uploaded_file.name}
        )
        print("Created document...")

        print("Chunking document...")
        text_splitter = RecursiveCharacterTextSplitter(
            separators = ["\n\n","\n","."," "],
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP,
        )
        chunks = text_splitter.split_documents([document])
        print(f"Created {len(chunks)} chunks.")

        print("Creating embedding model...")
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        print(f"Embedding and storing in Chroma collection '{collection_name}'...")
        vectorstore = Chroma.from_documents(
            documents = chunks,
            embedding = embeddings,
            collection_name = collection_name,
            persist_directory = CHROMA_DIR
        )

        print(f"Done. {vectorstore._collection.count()} vectors stored.")
        return collection_name

    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)