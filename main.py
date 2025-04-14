from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=2,
    topic="general",
    include_domains=["https://www.uz.ac.zw"],
)

checkpoint = MemorySaver()

with open("prompt.txt", "r") as f:
    prompt = f.read()

config = {"configurable": {"thread_id": "abc123"}}
agent = create_react_agent(llm, [tool], checkpointer=checkpoint, prompt=prompt)

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
