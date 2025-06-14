import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch, TavilyExtract
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import streamlit as st
import os
from auth import login_user

from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "uz_info_bot"

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, streaming=True)

# Initialize Tavily Search Tool
tavily_search_tool = TavilySearch(
    max_results=2,
    topic="general",
    include_domains=["https://www.uz.ac.zw", "https://en.wikipedia.org/wiki/University_of_Zimbabwe"]
)

tools = [tavily_search_tool]

st.title("UZ Info Bot 🤖")
st.logo("uz.jpg", link="https://www.uz.ac.zw", size="large")

# Authentication
username = login_user()

if username is None:
    st.stop()

# Use username for thread management
thread = {"configurable": {"thread_id": username}}

# Set up Prompt with 'agent_scratchpad'
today = datetime.datetime.today().strftime("%D")
prompt = """
You are a warm, welcoming, and helpful assistant that provides people with accurate, up-to-date information exclusively about the University of Zimbabwe (UZ). You have access to a web search tool that you can use to find relevant information directly from official or reliable sources, especially the University of Zimbabwe's website.
Keep your responses short and accurate. Do not mention you got the data from the website, just say 'from the information I found'.
When a user asks a question, use your web search tool to look for the most relevant and current information about the University of Zimbabwe. You may cover areas such as academic programs, admission procedures, faculties, student life, events, accommodation, staff directories, campus services, and more—but only if it's specifically about UZ.
If the retrieved information is not available or not directly relevant to the question, do not guess or hallucinate an answer. Be honest and let the user know you couldn't find what they're looking for, and if possible, suggest how they might find it.
Be friendly and conversational. Ask clarifying questions if needed and engage users in a supportive, interactive way to help them find what they need about UZ.
The current date is {today}.
Here is the user's username: {username}
"""

conn = sqlite3.connect('uz_chat.db', check_same_thread=False)
short_term_memory = SqliteSaver(conn)

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=prompt,
    checkpointer=short_term_memory
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Message"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    r1 = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        stream_mode="values",
        config=thread,
    )
    response = f"{r1['messages'][-1].content}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
