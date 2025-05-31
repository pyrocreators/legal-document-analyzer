from langchain.tools import tool
from utils import chunk_text, get_vector_store, load_vector_store, get_top_chunks
HARDCODED_STORE_PATH = "vectorstore/default_store"

@tool
def chunk_pdf_text(text: str) -> str:
    """Splits the input text into smaller chunks."""
    chunks = chunk_text(text)
    return "\n---\n".join(chunks[:10])  # Return a sample of chunks for brevity (5 first chunks returned)


@tool
def embed_and_store_single_input(text: str) -> str:
    """
       Embeds text and stores it in the vector store.
       """
    try:
        chunks = chunk_text(text)
        print(chunks)
        get_vector_store(chunks, HARDCODED_STORE_PATH)
        return f"Successfully embedded and stored vectors at {HARDCODED_STORE_PATH}."
    except Exception as e:
        return f"Error: {e}"

@tool
def qa_from_store(question: str) -> str:
    """
       Retrieves chunks relevant to a question from a stored vector database and returns them.
       """
    try:
        print(question, 'question')
        vectordb = load_vector_store(HARDCODED_STORE_PATH)
        results = get_top_chunks(question, vectordb)
        return "\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error: {e}"
