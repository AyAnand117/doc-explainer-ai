# Here we have retrieval pipeline
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "chroma_store"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_retriever(collection_name):
    print("Getting embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print("Loading Chroma collection...")
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR, 
        collection_name=collection_name, 
        embedding_function=embeddings,
        )

    print("Creating retriever...")
    retriever = vectorstore.as_retriever(search_kwargs={"k":4}) # returns top 4 chunks for every query
    return retriever