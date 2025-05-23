import streamlit as st
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from faiss import (
    IndexFlatL2
)
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
dimensions: int = len(embedding_function.embed_query("dummy"))

db = FAISS(
            embedding_function=embedding_function,
            index=IndexFlatL2(dimensions),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            normalize_L2=False
        )

vector = db.load_local("vector_updated", embeddings=embedding_function, allow_dangerous_deserialization=True)

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector.similarity_search(query, k=10)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tool = TavilySearch(
    max_results=3,
    topic="general",
    include_domains=["https://www.uz.ac.zw"],
)

checkpoint = MemorySaver()

with open("prompt.txt", "r") as f:
    prompt = f.read()

config = {"configurable": {"thread_id": "abc123"}}
agent = create_react_agent(llm, [retrieve, tool], checkpointer=checkpoint, prompt=prompt)

st.title("UZ Info Bot 🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    r1 = agent.invoke(
    {"messages": [{"role": "user", "content": prompt}]},
    stream_mode="values",
    config=config,
)
    response = f"{r1["messages"][-1].content}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
