import os
from pathlib import Path
import tempfile
from PIL import image
import pytesseract # OCR tool

from langchain_core.documents import Document
from lanchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "chroma_store"
COLLECTION = "yourdocs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

def ingest_image(uploaded_file):
    """
    Extracts text from an uploaded image using OCR, then chunks it,
    embeds it, and stores it in Chroma.
    """

    file_suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix =file_suffix) as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        temp_file_path = tmp_file.name

    try :
        print("Extracting text from image using OCR...")
        image = Image.open(temp_file_path)
        ext_text = pytesseract.image_to_string(image)
        if not ext_text.strip():
            raise ValueError("OCR extracted no text - image may not contain text or OCR failed")
        else:
            print("OCR complete. Extracted text:")
            print(text[:100])
        
        # Conversion to langchain document
        document = Document(
            page_content = ext_text,
            metadata = {"source":uploaded_file.name}
        )
        print("Created document...")

        print("Chunking document...")
        text_splitter = RecursiveCharacterTextSplitter(
            separator = ["\n\n","\n","."," "],
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP,
        )
        chunks = text_splitter.split_documents([document])
        print(f"Created {len(chunks)} chunks.")

        print("Creating embedding model...")
        embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        print(f"Embedding and storing in Chroma collection '{COLLECTION}'...")
        vectorstore = Chroma.from_documents(
            documents = chunks,
            embedding = embeddings,
            collection_name = COLLECTION,
            persist_directory = CHROMA_DIR
        )
        return f"Done. {vectorstore._collection.count()} vectors stored."

    except ValueError as e:
        return f"OCR Error: {str(e)}"
    except Exception as e:
        return f"Error processing image: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)