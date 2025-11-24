import streamlit as st

st.set_page_config(
    page_title="About Web-Researcher",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
# About Web-Researcher

**Web-Researcher** is an AI-powered research assistant designed to help you with your research tasks. It uses a team of AI agents to browse the web, gather information, and generate comprehensive reports on any given topic.

## How it Works

When you submit a research query, Web-Researcher's team of AI agents gets to work. Here's a simplified overview of the process:

1.  **Planning:** The AI planner agent analyzes your query and creates a step-by-step research plan.
2.  **Searching:** The AI search agents execute the plan, using tools like Google Search, Wikipedia, and Arxiv to find relevant information.
3.  **Synthesizing:** The AI synthesizer agent processes the gathered information, removes redundancies, and organizes it into a coherent narrative.
4.  **Reviewing:** The AI reviewer agent checks the synthesized report for quality and accuracy, and makes any necessary revisions.
5.  **Reporting:** The final report is presented to you in a clear and easy-to-read format. You can also download the report as a PDF.

## Features

-   **AI-Powered Research:** Leverage the power of large language models to automate your research tasks.
-   **Multi-Agent System:** A team of specialized AI agents work together to provide you with the best possible results.
-   **Multiple Search Tools:** The agents can use a variety of search tools to gather information from different sources.
-   **Interactive Interface:** A user-friendly interface that allows you to submit queries, monitor the research process, and view the final report.
-   **Downloadable Reports:** Download the research reports as PDF files for offline viewing and sharing.

## Get Started

To start a new research session, go to the **Home** page and enter your research query in the text box. The AI agents will take it from there!
"""
)
