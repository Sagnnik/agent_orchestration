from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from typing import TypedDict, Annotated, List
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langgraph.types import interrupt, Command
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
memory = MemorySaver()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

msg_prompt_template = HumanMessagePromptTemplate.from_template(
"""
X Topic: {x_topic}
Human Feedback: {feedback}

Generate a structured and well-written X post based on the given topic.

Consider previous human feedback to refine the reponse. 
"""
)

class AgentState(TypedDict):
    topic: str
    generated_post: Annotated[List[str], add_messages]
    human_feedback: Annotated[List[str], add_messages]


def chat_node(state: AgentState) -> AgentState:
    print("[Chat Node] Generating Content...")
    x_topic = state['topic']
    feedback = state.get("human_feedback", ["No Feedback yet"])

    prompt_messages = msg_prompt_template.format_messages(
        x_topic=x_topic,
        feedback=feedback[-1] if feedback else "No feedback yet"
    )
    messages = [SystemMessage(content="You are expert and savvy X post writer")] + prompt_messages
    response = model.invoke(messages)
    
    generated_post = response.content
    print(f"[chat_node] Generated post:\n{generated_post}\n")

    return {
        "generated_post": [AIMessage(content=generated_post)],
        "human_feedback": feedback
    }

def human_node(state:AgentState):
    """ Human Intervention Node --> Loops back to the chat model unless input is done """
    print("\n [Human Node] awaiting human feedback...")
    generated_post = state['generated_post']

    user_feedback = interrupt(
        {
            "generated_post": generated_post,
            "message": "provide feedback or type 'done' to finish"
        }
    )

    print(f"\n [Human Node] Received Human Feedback: {user_feedback}")

    if user_feedback.lower() == "done":
        return Command(
            goto="end_node",
            update={"human_feedback": state['human_feedback'] + ["Finalised"]}
        )
    
    return Command(
        goto="chat_node",
        update={"human_feedback": state['human_feedback'] + [user_feedback]}
    )

def end_node(state: AgentState): 
    """ Final node """
    print("\n[end_node] Process finished ✅.")
    print("Final Generated Post:", state["generated_post"][-1])
    print("Final Human Feedback", state["human_feedback"])
    return {"generated_post": state["generated_post"], "human_feedback": state["human_feedback"]}


graph = StateGraph(AgentState)

graph.add_node("chat_node", chat_node)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("chat_node")
graph.add_edge("chat_node", "human_node")
graph.set_finish_point("end_node")

app = graph.compile(checkpointer=memory)
config = {"configurable": {"thread_id": uuid4().hex}}

x_topic = input("Enter the X post topic: ")
initial_state = {
    "topic": x_topic,
    "generated_post": [],
    "human_feedback": []
}

for chunk in app.stream(initial_state, config=config):
    for node_id, value in chunk.items():
        if(node_id == "__interrupt__"):
            while True: 
                user_feedback = input("Provide feedback (or type 'done' when finished): ")
                app.invoke(Command(resume=user_feedback), config=config)

                if user_feedback.lower() == "done":
                    break
