import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# search_tool = TavilySearch(
#     max_results=5,
#     topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
# )

# class Movie(BaseModel):
#     """ A movie with details """
#     title: str = Field(..., description="Title of the movie")
#     year: int = Field(..., description="The year of release")
#     director: str = Field(..., description="The director of the movie")
#     rating: float = Field(..., description="The movie rating out of 10")

# model_with_structure = llm.with_structured_output(Movie, include_raw=True)
# response = model_with_structure.invoke("Provide details about the movie Inception")
# model = llm.bind_tools(tools=[search_tool])
# response = model.invoke("What is the weather at Kolkata today")
# print(response)
for chunk in model.stream("Why do parrots have colorful feathers?"):
    reasoning_steps = [r for r in chunk.content_blocks if r["type"] == "reasoning"]
    print(reasoning_steps if reasoning_steps else chunk.text)