# =============================================================================
# INSTRUCTOR DEMO SCRIPT — run these BEFORE opening the floor to students
# =============================================================================
# DEMO STEP 1 — "What is a vector?"
#   Run `python compare_embeddings.py`. Show the raw embedding for "apple"
#   (a list of ~1536 numbers) and the side-by-side distance comparison.
#   Point out: words with related MEANING sit close together in vector space,
#   even with no shared letters. This is the foundation for everything below.
#
# DEMO STEP 2 — "How the archive gets chopped up"
#   Run `python create_database.py` live (or show the printed summary if
#   already ingested). Open data/jedi_archives.md and show one chapter.
#   Explain: the document is split into hundreds of overlapping chunks —
#   when you query, you're searching THESE chunks, not the whole archive.
#
# DEMO STEP 3 — "Vague vs. specific — watch the score change"
#   Run this script and ask, live, in front of the room:
#     vague:    "tell me about the archive"
#                 -> low / middling scores, generic chunks come back
#     specific: "What did the Warden of the Eastern Gate say?"
#                 -> noticeably higher score, the real chunk surfaces
#   THIS is the core lesson: better question -> higher similarity score
#   -> better retrieval -> better answer. Point at the printed number.
#
# DEMO STEP 4 — "The full pipeline"
#   Show the printed prompt (retrieved chunks + question going to the LLM)
#   and the final response with sources. The LLM isn't reading the whole
#   archive — it only ever sees the chunks YOU retrieved. This demystifies
#   "the AI" and reframes the activity: you are driving a search engine
#   that feeds an LLM, not chatting with an oracle.
# =============================================================================

import sys
import time

# Force UTF-8 on stdout so emoji in the victory screen don't crash on Windows
# consoles whose default codepage (cp1252) can't encode them.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.align import Align
import pyfiglet
import openai
import os

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"
TOP_K = 3
VICTORY_PHRASE = "THE VERMILLION VECTOR"

# The verbatim strings that mark a genuine "you found it" moment — each
# appears exactly once in the whole archive. When one shows up in a retrieved
# excerpt, highlight it in green so students get an unmistakable visual signal
# that their query landed on something real (vs. just lore text).
#
# NOTE: the Chapter 39 "...was the Vermillion Gale." line is deliberately
# OMITTED even though it's a unique, quotable moment — it's the hunt's trap
# answer (confident, well-cited, and wrong). Highlighting it green would
# visually endorse the wrong answer and undercut the lesson that
# confident-sounding text isn't the same as correct text.
CLUE_PHRASES = [
    "Find the Silver Data Librarian. Hall of Lost Embeddings.",
    "Check under the Compass Rose. The cartographer left a confession.",
    "THE VERMILLION VECTOR",
    "We don't know. That is the answer.",
    # The simple chain (Brod the Glorious King -> ... -> Elder Nova) has no
    # traps, so every bridge-name/pointer below is safe to highlight green —
    # each one really does point a seeker to their next stop.
    "BROD THE GLORIOUS KING",
    "GIANT COOKIE JAR",
    "DJ SPARKLES",
    "MOONLIGHT DOOR",
    "GRANDPA GIZMO",
    "PROFESSOR PICKLES",
    "CRYSTAL CAVERN",
    "BUBBLES THE ROBOT",
    "SINGING STATUE",
    "ELDER NOVA",
]


def highlight_clues(snippet):
    for phrase in CLUE_PHRASES:
        if phrase in snippet:
            snippet = snippet.replace(phrase, f"[bold green]{phrase}[/bold green]")
    return snippet

PROMPT_TEMPLATE = """
You are an archive-spirit of the AI Lodge Jedi Order. A seeker has come to you
for help finding something hidden within the Lodge's classified archives.
Answer the seeker's question using ONLY the archive excerpts given below —
never invent details that are not present in them. If the excerpts don't
contain the answer, say so plainly rather than guessing; the Lodge does not
hallucinate like the Empire does.

Archive excerpts:

{context}

---

The seeker asks: {question}

Answer as the archive-spirit, citing what the excerpts actually say:
"""

console = Console(legacy_windows=False)


def main():
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    model = ChatOpenAI(model="gpt-4o-mini")

    console.print(
        "\n[bold cyan]The AI Lodge Jedi Order Archives[/bold cyan]\n"
        "Ask the archive-spirit anything. Type [bold]exit[/bold] to leave the archive.\n"
    )

    while True:
        query_text = input("seeker> ").strip()

        if not query_text:
            continue
        if query_text.lower() in ("exit", "quit"):
            console.print("\n[dim]The archive doors close behind you...[/dim]\n")
            break

        if query_text.upper() == VICTORY_PHRASE:
            show_victory_screen()
            continue

        run_query(db, model, query_text)


def run_query(db, model, query_text):
    results = db.similarity_search_with_relevance_scores(query_text, k=TOP_K)

    if len(results) == 0:
        console.print("[yellow]The archive returns nothing for that query.[/yellow]\n")
        return

    console.print(f"\n[bold]Retrieved {len(results)} excerpts:[/bold]")
    for rank, (doc, score) in enumerate(results, start=1):
        source = doc.metadata.get("source", "Unknown chapter")
        snippet = doc.page_content.strip().replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        snippet = highlight_clues(snippet)
        console.print(
            f"  [bold]#{rank}[/bold]  "
            f"[bold green]score: {score:.4f}[/bold green]  "
            f"[cyan]({source})[/cyan]"
        )
        console.print(f"        \"{snippet}\"")
    console.print()

    context_text = "\n\n---\n\n".join(doc.page_content for doc, _score in results)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    response_text = model.predict(prompt)
    console.print(f"[bold magenta]Archive-spirit:[/bold magenta] {response_text}\n")


def show_victory_screen():
    console.clear()
    width = console.size.width

    art = pyfiglet.figlet_format("RAG MODEL GOAT", font="standard")
    art_text = Text(art, style="bold yellow")

    console.print(Align.center(art_text, width=width))
    console.print()

    lines = [
        ("THE HALLUCINATION EMPIRE HAS FALLEN", "bold red"),
        ("THE AI LODGE RISES", "bold green"),
        ("YOU ARE NOW A RAG MODEL GOAT \U0001F3C6", "bold yellow"),
        ("MAY THE RAG BE WITH YOU, PADAWAN", "bold green"),
    ]

    for text, style in lines:
        console.print(Align.center(Text(text, style=style)))
        time.sleep(0.6)

    console.print()
    console.print(Align.center(Text("=" * min(width, 60), style="bold yellow")))
    console.print()


if __name__ == "__main__":
    main()
