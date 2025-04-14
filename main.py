from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from faiss import (
    IndexFlatL2
)
from langchain_community.docstore.in_memory import (
    InMemoryDocstore
)
from langchain_community.vectorstores import FAISS
import streamlit as st # adjust this import based on your setup
import time
from dotenv import load_dotenv

load_dotenv()

embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

dimensions: int = len(embedding_function.embed_query("dummy"))
db = FAISS(
            embedding_function=embedding_function,
            index=IndexFlatL2(dimensions),
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            normalize_L2=False
        )

vector = db.load_local("uz", embeddings=embedding_function, allow_dangerous_deserialization=True)

from langchain_core.tools import tool

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector.similarity_search(query)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=2,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    include_domains=["https://www.uz.ac.zw"],
    # exclude_domains=None
)

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

checkpoint = MemorySaver()

prompt = """
You are a chatbot that provides information to users who want to know about the University of Zimbabwe, and keeping
up with current information. Topics of questions may range from admissions, general information about the university,
and the school current affairs.
First greet the user warmly and ask them if they have any questions,
be ready to answer their questions and use retrieve tool to get information. If a question is irrelevant,
address to the user that it is irrelevant. Follow a friendly, conversational tone.
 """

config = {"configurable": {"thread_id": "abc123"}}
agent = create_react_agent(llm, [tool], checkpointer=checkpoint, prompt=prompt)

import streamlit as st
import time

st.title("UZ Help Desk Bot")

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
