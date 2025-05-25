import datetime

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_tavily import TavilySearch, TavilyExtract
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, streaming=True)

# Initialize Tavily Search Tool
tavily_search_tool = TavilySearch(
    max_results=5,
    topic="general",
)
# Initialize Tavily Extract Tool
tavily_extract_tool = TavilyExtract()

tools = [tavily_search_tool, tavily_extract_tool]

# Set up Prompt with 'agent_scratchpad'
today = datetime.datetime.today().strftime("%D")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You are a helpful reaserch assistant, you will be given a query and you will need to
    search the web for the most relevant information then extract content to gain more insights. The date today is {today}."""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for tool calls
])
# Create an agent that can use tools
agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Create an Agent Executor to handle tool execution
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

user_input =  "Research the latest developments in quantum computing and provide a detailed summary of how it might impact cybersecurity in the next decade."

# Construct input properly as a dictionary
response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})

# st.title("UZ Info Bot 🤖")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # React to user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     r1 = agent.invoke(
#     {"messages": [{"role": "user", "content": prompt}]},
#     stream_mode="values",
#     config=config,
# )
#     response = f"{r1["messages"][-1].content}"
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         st.markdown(response)
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})
