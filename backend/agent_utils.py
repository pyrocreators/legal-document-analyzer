from utils import read_pdf
from agent_executor import agent_executor

def process_pdf_and_respond_with_agent(pdf_path):
    text = read_pdf(pdf_path)
    hardcoded_question = "Summarize the content of this document."

    plan_prompt = f"""
You are a legal document analyzer agent. Please:
1. Embed and store this text in a vector store.
2. Then, answer the question based on the stored data.

Use this format for both steps: <text or question>::<store_path>.

Question: {hardcoded_question}

Here is the document content:
{text[:4000]}  # truncated for token limit
"""
    return agent_executor.run(plan_prompt)
