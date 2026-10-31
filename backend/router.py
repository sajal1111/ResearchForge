from langchain.agents import create_agent
from langchain.tools import tool
from agents import llm
from pipeline import run_research_pipeline


@tool
def run_research(topic: str) -> str:
    """
    Run the full research pipeline (search -> scrape -> write -> critique) on a topic
    and return the final report with critic feedback.

    USE THIS TOOL when the user asks for a research report, deep dive, analysis,
    summary, or structured writeup on a specific subject, technology, person,
    event, or question that requires searching the web and synthesizing sources.

    DO NOT use this tool for:
    - Greetings or small talk ("hi", "how's it going", "thanks")
    - Questions about the assistant itself ("what can you do", "who are you")
    - Simple facts answerable without research ("what is 2+2", "what does API stand for")
    - Follow-up chat about a report already produced earlier in the conversation
      (this tool has no memory of prior runs — it always starts a fresh pipeline)

    Args:
        topic: The research topic or question, taken as close to the user's own
            wording as possible. Don't over-rephrase — the pipeline searches on
            this string directly.

    Returns:
        A string containing the generated report and the critic's feedback.
    """
    state = run_research_pipeline(topic)
    return (
        f"REPORT:\n{state['report']}\n\n"
        f"CRITIC FEEDBACK:\n{state['feedback']}"
    )


ROUTER_SYSTEM_PROMPT = """You are the front-desk assistant for a research tool.

For every user message, decide:
1. Casual chitchat, greetings, or meta questions about you -> reply directly yourself. Do NOT call any tool.
2. A genuine research request -> call the `run_research` tool with the topic, then present its output to the user.

Rules:
- Never call `run_research` for chitchat.
- Never write a research report from your own knowledge — you have no live search access; only the tool does. Always delegate real research requests to it.
- If unsure whether something counts as a research request, prefer asking a brief clarifying question over guessing.
"""

router_agent = create_agent(
    model=llm,
    tools=[run_research],
    system_prompt=ROUTER_SYSTEM_PROMPT,
)

