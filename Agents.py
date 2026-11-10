from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search,scrape_url
import os
from dotenv import load_dotenv
load_dotenv()

# model set up
llm = ChatOpenAI(model = 'gpt-4o-mini',temperature=0)

# creating agents for web_search
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )

# creating agents for scrape_url
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )

# writer chain with write_prompt
writer_prompt = ChatPromptTemplate.from_messages([
    ("system","You are an expert research writer. Write clear , structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
    Topic : {topic}
    Research Gathered : {research}
    Structure the report as:
    - Introduction 
    - Key Findings (Minimum 3 well explained points)
    - Conclusion
    - Sources (List all urls found in the research)

    Be detailed , factual and professional.""")
    ])

writer_chain = writer_prompt | llm | StrOutputParser()

# Critic chain with critic_prompt
critic_prompt = ChatPromptTemplate([
    ("system","You are a sharp and constructive research critic. Be honest and specific"),
    ("human","""Review the research report below and evaluate it strictly.
    Report: {report}

    Responde in this exact format:
    Score: x/10

    Strenths:
    -...
    -...

    Areas to improve:
    -...
    -...

    One line verdict:
    ...              """)
])

critic_chain = critic_prompt | llm | StrOutputParser()