# The AI Lodge Jedi Order Archives — RAG Treasure Hunt

You are a seeker of the AI Lodge. Somewhere inside a long classified archive
lies a hidden chain of clues leading to a secret prize. The archive is far too
long to paste into ChatGPT — the only way through is to query it the way the
Lodge does: with retrieval-augmented generation (RAG) and semantic vector
search.

The first few seekers to find the final answer and type it into the archive
win the prize. Follow the steps below **in order** — each one is a command you
can copy and paste straight into your terminal.

---

## Step 0 — Check your Python version

Run:

```
python --version
```

Any reasonably recent Python 3 (this has been built and tested on **3.14**)
should work fine. If `pip install` later complains about a missing compiler
("Rust", "Microsoft Visual C++ 14.0", "gcc") — that's the only time Python
version becomes relevant — see the troubleshooting note in Step 3 below.

## Step 1 — Open this folder in your terminal

Make sure your terminal's current folder is this one (the one this README is
in — it should contain `hunt.py`, `requirements.txt`, etc).

## Step 2 — Create a virtual environment

This keeps this project's packages separate from everything else on your
computer.

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
> Getting a "running scripts is disabled" error? Open PowerShell **as
> Administrator** once and run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
> Then close that window and try the two commands above again in a normal
> terminal.

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ You'll know it worked when your terminal prompt starts with `(venv)`.
**Every time you open a new terminal for this project, activate the venv again
using the second command above before doing anything else.**

## Step 3 — Install the project's packages

```
pip install -r requirements.txt
```

This pulls in everything the project needs: LangChain, ChromaDB (the vector
database), the OpenAI SDK, and the libraries used for the victory screen.

**If a package fails to install:** this is almost always pip trying to *build
a package from source* instead of downloading a ready-made version, usually
because your Python is newer than the pinned package expects. The error will
mention something like "can't find Rust compiler", "Microsoft Visual C++ 14.0
is required", or "command 'gcc' failed". The fix is the same every time —
install the *one* complaining package by itself first (letting pip pick a
newer, compatible version), then re-run the main install:

```
pip install --only-binary=:all: tiktoken
pip install -r requirements.txt
```

(If a different package is the one complaining, swap its name in for
`tiktoken` above.)

## Step 4 — Add your OpenAI API key

1. Copy the example env file:
   - **Windows:** `copy .env.example .env`
   - **Mac/Linux:** `cp .env.example .env`
2. Open the new `.env` file in a text editor and replace `sk-...` with your
   real OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-real-key-here
   ```

You'll need an OpenAI account with a small amount of credit on it — building
the archive's database and asking it questions both make small, low-cost calls
to the OpenAI API.

⚠️ **Never share your `.env` file or your API key with anyone** (it's already
listed in `.gitignore`, so a normal `git` workflow won't pick it up by
accident).

## Step 5 — Build the archive's vector database

This is the big one — it reads the archive, chops it into chunks, turns each
chunk into a vector embedding via the OpenAI API, and stores everything in a
local database folder called `chroma/`.

```
python create_database.py
```

Run this **once**. It will print its progress and finish with a summary like:

```
Ingested 431 chunks from 61 chapters into 'chroma/'.
```

If you ever need to rebuild it from scratch, delete the `chroma/` folder
first — the script deliberately refuses to overwrite an existing one (since
rebuilding re-embeds everything and re-bills your OpenAI account).

## Step 6 — Enter the archive

```
python hunt.py
```

This opens an interactive prompt where you can ask the archive-spirit
anything. For every question you type, it shows you:

- the **similarity score** of each retrieved excerpt (higher = closer match in
  *meaning* to your question — watch this number, it's your compass)
- which **chapter** each excerpt came from
- the archive-spirit's answer, generated only from what it actually retrieved

Type `exit` or `quit` to leave the archive at any time.

---

## How to actually win

1. Your instructor will read out a starting question. Type it in.
2. Read what comes back carefully. Somewhere in the retrieved excerpt there
   will be a **name, place, or thing** that wasn't in your question — often
   shown in capital letters, and lit up in **green** when it's a real find.
3. Ask a short, natural question *about that thing* — "Who is ___?", "What did
   ___ say?", "Why does ___ ___?", "How does ___ ___?" — and see where it takes
   you.
4. Repeat. Each answer hands you the next question. Follow the thread.
5. When you find the final phrase, type it into the prompt **exactly** as it
   appears in the archive (it's not case-sensitive, but every word must
   match). Get it right, and the archive will let you know. 🏆

## Tips for the hunt

- Vague questions return vague, low-scoring results. Specific, well-phrased
  questions score higher and retrieve sharper excerpts — use that signal to
  steer your search.
- The archive is full of long, sprawling lore. Not everything that *sounds*
  confident and well-cited is actually correct — read critically.
- Speed matters as much as accuracy. The first ones to reach the true final
  answer win — so don't get stuck rereading the same excerpt forever. If a
  question isn't getting you anywhere new after a couple of tries, try
  rephrasing it or asking about a different name from your last result.

May the RAG be with you. 🏆
