from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Sequence, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph = StateGraph(AgentState)
agent = graph.compile()

def start_agent(query, max_results, depth):
    pass
