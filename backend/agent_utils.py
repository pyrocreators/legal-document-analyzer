from utils import read_pdf
from agent_executor import agent_executor
from langsmith import traceable


@traceable
def process_pdf_and_with_summary(pdf_path):
    text = read_pdf(pdf_path)

    hardcoded_question = (
        "Analyze the document and provide a brief summary that includes only:\n"
        "1. The type of document (e.g., NDA, employment contract, service agreement).\n"
        "2. The expiration date, if mentioned.\n"
        "Respond in the same language as the document."
    )

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


@traceable
def process_pdf_and_with_key_points(pdf_path):
    text = read_pdf(pdf_path)

    hardcoded_question = (
        "Summarize the key points from this document. "
        "If this is a legal document, especially an NDA, highlight the restrictions using the format: "
        "'Key Point Name - Description'. "
        "Respond in the same language as the document."
    )

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

