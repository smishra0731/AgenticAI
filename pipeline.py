from Agents import build_reader_agent, build_search_agent,writer_chain, critic_chain

def run_research_pipeline(topic:str)-> dict:
    state = {}
    # Step 1 Search agent working
    print("******************************************************************")
    print("step - 1 search agent is working")
    print("******************************************************************")

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    print("\n Search Result", state["search_results"])

    # Step 2 Reader agent working
    print("******************************************************************")
    print("step - 2 reader agent is scraping top resources...")
    print("******************************************************************")

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
    "messages": [(
        "user",
        f"Based on the following search results about '{topic}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nScraped content\n", state['scraped_content'])

    # Step 3 writer chain
    print("******************************************************************")
    print("step - 3 writer is drafting the result...")
    print("******************************************************************")

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']}\n\n"
        f"DETAILED SCRAPE CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\nFinal Report:\n",state["report"])

    # Step 4 critic will review report
    print("******************************************************************")
    print("step - 4 critic will review rthe report...")
    print("******************************************************************")

    state["feedback"] = critic_chain.invoke({
        "report" : state["report"]
    })

    print("\nCritic Report:\n", state["feedback"])

    return state


if __name__=="__main__":
    topic = input("\n Enter a research topic: ")
    run_research_pipeline(topic)