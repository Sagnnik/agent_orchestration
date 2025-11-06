from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain_tavily import TavilySearch
from typing import Sequence, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

search_tool = TavilySearch()
memory = MemorySaver()
system_prompt = (
    "You have access to a web search tool. ONLY call tools when the user "
    "explicitly asks for web/search/news/current data, or when answering "
    "requires up-to-date facts you cannot know. For greetings, identities, "
    "small talk, or general knowledge, DO NOT CALL ANY TOOLS."
)

model = ChatOllama(model='llama3.2', temperature=0).bind_tools([search_tool])

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def chat_node(state: AgentState) -> AgentState:
    #msgs = [SystemMessage(content=system_prompt)] + list(state["messages"])  # For larger models just add the system prompt at the start
    response = model.invoke(state["messages"])
    print("\n", response.content)
    return {"messages": [response]}

def tool_router(state: AgentState):
    last_msg = state['messages'][-1]

    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tool_node"
    return "end"
    
tool_node = ToolNode(tools=[search_tool])

graph=StateGraph(AgentState)

graph.add_node("chat_node", chat_node)
graph.add_node("tool_node", tool_node)

graph.set_entry_point("chat_node")

graph.add_conditional_edges("chat_node", tool_router, {"tool_node": "tool_node", "end": END})
graph.add_edge("tool_node", "chat_node")

app=graph.compile(checkpointer=memory)
app.get_graph().print_ascii()

config = {"configurable": {
    "thread_id": 1
}}


while True:
    user_input = input("USER: ")
    if user_input.strip() == '/bye':
        break
    final_state = app.invoke(
        {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]},
        config=config
    )
    # last = final_state["messages"][-1]
    # print("AI:", getattr(last, "content", last))