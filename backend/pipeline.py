from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain
from tools import web_search, scrape_url
import re
from ranking import parse_search_results, rank_sources
from cache import cached_web_search, cached_scrape_url
import asyncio
from agents import plan_subtopics
from config import TOP_N_SOURCES_TO_SCRAPE
from report_modes import get_mode_instructions
from config import DEFAULT_REPORT_MODE
from ranking import parse_search_results, rank_sources, dedupe
from agents import writer_chain, critic_chain, plan_subtopics, summarize_page


async def _parallel_search(subtopics: list[str]) -> dict[str, str]:
    """
    Run web_search concurrently across subtopics. Each call still goes through
    the cache (Step 3), so repeated subtopics across runs are cheap.

    Returns {subtopic: raw_search_result_string}.
    """
    async def search_one(subtopic: str) -> tuple[str, str]:
        result = await asyncio.to_thread(cached_web_search, web_search, subtopic)
        return subtopic, result

    pairs = await asyncio.gather(*(search_one(s) for s in subtopics))
    return dict(pairs)

async def _parallel_scrape(urls: list[str]) -> dict[str, str]:
    """
    Scrape multiple URLs concurrently. Each call goes through the page cache.
    Returns {url: scraped_text}.
    """
    async def scrape_one(url: str) -> tuple[str, str]:
        result = await asyncio.to_thread(cached_scrape_url, scrape_url, url)
        return url, result

    pairs = await asyncio.gather(*(scrape_one(u) for u in urls))
    return dict(pairs)

def _format_sources_for_writer(scraped_by_url: dict[str, str]) -> str:
    """
    Build a numbered '[1] url' list from the scraped sources, so the writer
    can cite [1], [2] etc. and we can trust references map to real URLs
    that were actually scraped -- not hallucinated.
    """
    if not scraped_by_url:
        return "No sources available."

    return "\n".join(
        f"[{i}] {url}" for i, url in enumerate(scraped_by_url.keys(), start=1)
    )


def run_research_pipeline(topic: str, mode: str = DEFAULT_REPORT_MODE) -> dict:
    """
    Run the research pipeline end-to-end for a single topic: plan -> parallel
    search -> rank -> parallel scrape -> write -> critique. Returns the
    accumulated state dict.

    This is a plain function, not an agent -- called directly by pipeline
    internals, and by router.py's `run_research` tool.
    """
    state = {}

    # step 1 - plan subtopics + parallel search
    print("\n" + " ="*50)
    print("step 1 - planning subtopics and searching in parallel ...")
    print("="*50)

    subtopics = plan_subtopics(topic)
    state["subtopics"] = subtopics
    print("\n subtopics:", subtopics)

    search_results_by_subtopic = asyncio.run(_parallel_search(subtopics))
    state["search_results_by_subtopic"] = search_results_by_subtopic

    for subtopic, result in search_results_by_subtopic.items():
        print(f"\n--- search result for '{subtopic}' ---\n{result}")

    # Combined string for ranking/writer -- both expect one blob of
    # "Title/URL/Snippet" blocks.
    state["search_results"] = "\n----\n".join(search_results_by_subtopic.values())

    # rank sources (pure python, no LLM)
    parsed_sources = parse_search_results(state["search_results"])
    deduped_sources = dedupe(parsed_sources)
    print(f"\n sources: {len(parsed_sources)} found -> {len(deduped_sources)} after dedupe")

    ranked_sources = rank_sources(deduped_sources, query=topic)

    state["ranked_sources"] = ranked_sources

    print("\n ranked sources (best first):")
    for s in ranked_sources:
        print(f"  [{s['score']}] {s['url']}")

    # step 2 - parallel scrape top N ranked sources
    print("\n" + " ="*50)
    print(f"step 2 - scraping top sources in parallel ...")
    print("="*50)

    top_urls = [s["url"] for s in ranked_sources[:TOP_N_SOURCES_TO_SCRAPE]]

    scraped_by_url = asyncio.run(_parallel_scrape(top_urls)) if top_urls else {}
    state["scraped_by_url"] = scraped_by_url

    for url, content in scraped_by_url.items():
        print(f"\n--- scraped content for {url} ---\n{content[:300]}...")

    print("\n" + " ="*50)
    print("step 2b - summarizing scraped pages ...")
    print("="*50)

    summarized_by_url = {
        url: summarize_page(topic, content)
        for url, content in scraped_by_url.items()
    }
    state["summarized_by_url"] = summarized_by_url

    for url, summary in summarized_by_url.items():
        print(f"\n--- summary for {url} ---\n{summary}")


    # Combined text for the writer, same shape it expected before (one blob).
    state["scraped_content"] = "\n\n".join(
        f"SOURCE: {url}\n{summary}" for url, summary in summarized_by_url.items()
    ) or "No content scraped."

    # step 3 - writer chain
    print("\n" + " ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["sources_list"] = _format_sources_for_writer(summarized_by_url)
    state["mode"] = mode

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
        "sources": state["sources_list"],
        "mode_instructions": get_mode_instructions(mode)
    })

    print("\n Final Report\n", state['report'])

    # step 4 - critic
    print("\n" + " ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state


# if __name__ == "__main__":
#     topic = input("\n Enter a research topic : ")
#     run_research_pipeline(topic)

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    mode = input("Enter report mode (quick_summary/deep_research/technical/business/interview_prep) [default deep_research]: ").strip() or "deep_research"
    run_research_pipeline(topic, mode=mode)