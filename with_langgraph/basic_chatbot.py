from langchain_ollama.chat_models import ChatOllama
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from datetime import datetime, timezone

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = ChatOllama(model="llama3.2")
# response = llm.invoke("What is the capital of France?")
# print(response)

def process(state: AgentState) -> AgentState:
    reponse = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=reponse.content))
    print(f"\nAI: {reponse.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = []
user_input = input("\nEnter the input: ")
while user_input !="/bye":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result['messages']
    user_input = input("Enter the input: ")

now = datetime.now(timezone.utc)
humanformat = now.strftime('%Y-%m-%d %H:%M:%S %Z%z')
with open("logging.txt", 'w') as f:
    f.write(f"Last Conversation Log at [{humanformat}]: \n")
    for msg in conversation_history:
        if isinstance(msg, HumanMessage):
            f.write(f"You: {msg.content}\n")
        elif isinstance(msg, AIMessage):
            f.write(f"AI: {msg.content}\n\n")
    f.write("End of conversation")

print("Conversation saved to logging.txt")
