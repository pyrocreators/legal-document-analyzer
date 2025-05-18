from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from agents import chunk_pdf_text, embed_and_store_single_input, qa_from_store

llm = ChatOpenAI(model="gpt-4o-mini")

tools = [chunk_pdf_text, embed_and_store_single_input, qa_from_store]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
