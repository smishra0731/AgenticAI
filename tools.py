from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
import sys
from dotenv import load_dotenv
load_dotenv()

#Groq model="openai/gpt-oss-120b"

tavily = TavilyClient(api_key = os.getenv("TAVILY_API_KEY")) 

@tool
def web_search(query:str) -> str:
    """Search the web for recent and realiable information on a topic . Returns Titles , URLs and snippets"""
   # results = tavily.search(query=query,max_results=5)
    try:
      results = tavily.search(query=query, max_results=5, search_depth="basic")
    except Exception as e:
      return f"Search failed: {e}"
    out = []

    for r in results["results"]:
        out.append(
            f"Title: {r["title"]}\nURL: {r["url"]}\nSnippet: {r["content"][:300]}\n"
        )
    return "\n-----\n".join(out)

#print(web_search.invoke("What are the latest news on war...?"))

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given url for deeper reading."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav","footer"]):
            tag.decompose()
        return soup.get_text(separator = " ", strip=True)[:3000]       
    except Exception as e:
        return f"Could not scrape url: {str(e)}"

#print(scrape_url.invoke("https://www.bbc.com/sport/cricket"))
