from utils import read_pdf
from agent_executor import agent


async def process_pdf_and_respond_with_agent(pdf_path):
    text = read_pdf(pdf_path)
    question = "Summarize the content of this document."

    prompt = f"""Please analyze this document:
1. Embed and store the text in a vector store
2. Answer this question: {question}

Document content (truncated):
{text[:4000]}
"""
    return await agent.process_prompt(prompt)