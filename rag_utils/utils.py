import os
import fitz
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langsmith import traceable

load_dotenv()

VECTOR_DIR = "vectorstore"
os.makedirs(VECTOR_DIR, exist_ok=True)
HARDCODED_STORE_PATH = os.path.join(VECTOR_DIR, "default_store")

VECTOR_DIR = "vectorstore"
os.makedirs(VECTOR_DIR, exist_ok=True)

def read_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    for page in pdf_document:
        text += page.get_text() + '\n'
    pdf_document.close()
    return text

@traceable
def chunk_text(text):
    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)

def get_vector_store(chunks, store_path=HARDCODED_STORE_PATH):
    import os
    os.makedirs(store_path, exist_ok=True)
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_texts(chunks, embeddings)
    vectordb.save_local(store_path)
    return vectordb

def load_vector_store(store_path=HARDCODED_STORE_PATH):
    embeddings = OpenAIEmbeddings()
    if not os.path.exists(store_path):
        raise FileNotFoundError(f"Vector store path not found: {store_path}")
    return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)


@traceable
def get_top_chunks(prompt, vectordb, k=4):
    return vectordb.similarity_search(prompt, k=k)