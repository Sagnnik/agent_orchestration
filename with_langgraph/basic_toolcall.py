from langchain_ollama.chat_models import ChatOllama
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from datetime import datetime, timezone

llm = ChatOllama(model="llama3.2")

# add_messages is a reducer function that just appends messages of same type
# BaseMessage is the parent class of all types of messages
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a:int, b:int):
    """This is an addition function that adds 2 numbers"""

    return a+b

@tool
def sub(a:int, b:int):
    """This is a substraction function that substracts 2 numbers"""

    return a-b

@tool
def multiply(a:int, b:int):
    """This is a multiplication function that multiplies 2 numbers"""

    return a*b

tools = [add, sub, multiply]

model = ChatOllama(model="llama3.2").bind_tools(tools)

def model_call(state: AgentState)-> AgentState:
    system_prompt = SystemMessage(content="You are my ai assistant. PLease answer my queries to the best of your abilities")
    response = model.invoke([system_prompt]+ state["messages"])
    #print(state['messages'])
    return {"messages": [response]}     # this returns the updated state and the reducer function handles the appeding

def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
graph = StateGraph(AgentState)

graph.add_node("agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")

app=graph.compile()

def print_stream(stream):
    for s in stream:
        msg = s['messages'][-1]
        if isinstance(msg, tuple):
            print(msg)
        else:
            msg.pretty_print()

inputs = {"messages": [("user", "add 100 + 55 and then multiply the result with 15. Tell me a joke")]}
print_stream(app.stream(inputs, stream_mode="values"))