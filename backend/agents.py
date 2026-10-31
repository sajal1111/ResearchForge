from langchain.agents import create_agent
# from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
# from langchain_cerebras import ChatCerebras
from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv
import re

load_dotenv()

#model setup 
llm = ChatOpenRouter(
    model="gpt-oss-120b", 
    max_tokens=1400,
    temperature=0.25
)

light_llm = ChatMistralAI(
    model="mistral-small-2506",
    max_tokens=800,
    temperature=0.2
)


#1st agent 
def build_search_agent():
    return create_agent(
        model = light_llm,
        tools= [web_search]
    )

#2nd agent 
def build_reader_agent():
    return create_agent(
        model = light_llm,
        tools = [scrape_url]
    )
##i think i would not use them bcz they are making llm calls and tokens get used
#i will just directly call the tools 

#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and "
               "insightful reports. You only cite sources from the provided list -- "
               "never invent or guess a URL."),
    ("human", """Topic: {topic}

Research Gathered:
{research}

Available Sources (cite ONLY from this list, using the exact URLs given):
{sources}

{mode_instructions}

Use inline citations like [1], [2] matching the source list where relevant,
and end with a References section listing only the sources you actually cited."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | light_llm | StrOutputParser()

from config import SUBTOPIC_COUNT

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research planning assistant. You break broad topics into "
               "focused, non-overlapping subtopics that together give good coverage "
               "for a research report."),
    ("human", """Break the topic below into exactly {count} focused subtopics suitable
for separate web searches. Each should be specific enough to search on its own,
and together they should cover the topic well without heavy overlap.

Topic: {topic}

Respond with ONLY a numbered list, one subtopic per line, nothing else. Example format:
1. First subtopic
2. Second subtopic"""),
])

planner_chain = planner_prompt | light_llm | StrOutputParser()


def plan_subtopics(topic: str, count: int = SUBTOPIC_COUNT) -> list[str]:
    """
    Single LLM call that breaks a topic into `count` focused subtopics for
    separate searches. Plain function -- no create_agent, no tools, no branching.

    Falls back to [topic] itself if parsing yields nothing usable, so downstream
    parallel search always has at least one query to run.
    """
    raw = planner_chain.invoke({"topic": topic, "count": count})

    subtopics = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading numbering like "1.", "1)", "- "
        cleaned = re.sub(r"^\s*(\d+[\.\)]|-)\s*", "", line).strip()
        if cleaned:
            subtopics.append(cleaned)

    return subtopics[:count] if subtopics else [topic]


from config import SUMMARY_TARGET_WORDS

summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You summarize web page content into concise, information-dense "
               "notes for a research writer. Output only the summary -- no "
               "commentary, no preamble."),
    ("human", """Summarize the content below in about {target_words} words. Keep
only facts, figures, and claims relevant to the topic. Discard boilerplate,
navigation text, and anything off-topic.

Topic: {topic}

Content:
{content}"""),
])

summarizer_chain = summarizer_prompt | light_llm | StrOutputParser()


def summarize_page(topic: str, content: str, target_words: int = SUMMARY_TARGET_WORDS) -> str:
    """
    Plain LLM call that condenses one scraped page into a short, topic-focused
    summary. Keeps writer input small instead of feeding full raw pages.
    """
    if not content or content.startswith("Could not scrape"):
        return content  # nothing useful to summarize, pass through as-is
    return summarizer_chain.invoke({
        "topic": topic,
        "content": content,
        "target_words": target_words
    })
