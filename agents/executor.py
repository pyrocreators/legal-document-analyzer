from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from agents.tools import chunk_pdf_text, embed_and_store_single_input, qa_from_store

llm_model = "gpt-4o-mini"


chunk_agent = create_react_agent(
    model=f"openai:{llm_model}",
    tools=[chunk_pdf_text],
    prompt="You are an agent that splits large text documents into smaller chunks.",
    name="chunk_agent"
)

embed_agent = create_react_agent(
    model=f"openai:{llm_model}",
    tools=[embed_and_store_single_input],
    prompt="You are an agent that embeds text chunks and stores them in a vector database.",
    name="embed_agent"
)

qa_agent = create_react_agent(
    model=f"openai:{llm_model}",
    tools=[qa_from_store],
    prompt="You are an agent that answers questions by querying the stored vector database.",
    name="qa_agent"
)

supervisor = create_supervisor(
    agents=[chunk_agent, embed_agent, qa_agent],
    model=ChatOpenAI(model=llm_model),
    prompt=(
        "You are a supervisor managing three agents: chunk_agent, embed_agent, and qa_agent. "
        "Based on the user's query, delegate the task to the most appropriate agent."
    )
).compile()


def run_supervisor_with_text(text, question, store_path="vector_store"):
    chunk_input = text
    print("Chunking text:")
    for chunk in chunk_agent.stream({"messages": [{"role": "user", "content": chunk_input}]}):
        print(chunk)
    print("\n")

    embed_input = text
    print("Embedding and storing:")
    for chunk in embed_agent.stream({"messages": [{"role": "user", "content": embed_input}]}):
        print(chunk)
    print("\n")

    qa_input = question
    print("Querying stored data:")
    for chunk in qa_agent.stream({"messages": [{"role": "user", "content": qa_input}]}):
        return chunk['agent']['messages'][0]['content']
    print("\n")


