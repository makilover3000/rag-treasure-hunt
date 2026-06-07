from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import openai
import os
import re

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

CHROMA_PATH = "chroma"
DATA_PATH = "data/jedi_archives.md"

# Matches headings like "# Chapter 7: The Eastern Gate Records"
CHAPTER_PATTERN = re.compile(r"^# (Chapter \d+(?:\.\d+)?: .+)$", re.MULTILINE)

EMBED_BATCH_SIZE = 50


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    """Read the archive file and split it into one Document per chapter,
    tagging each chapter's text with its own heading as the `source`."""
    with open(DATA_PATH, encoding="utf-8") as f:
        text = f.read()

    matches = list(CHAPTER_PATTERN.finditer(text))
    if not matches:
        raise ValueError(
            f"No '# Chapter N: <Title>' headings found in {DATA_PATH}. "
            "Check that the document follows the required heading format."
        )

    documents = []
    for i, match in enumerate(matches):
        title = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_text = text[start:end].strip()
        documents.append(Document(page_content=chapter_text, metadata={"source": title}))

    print(f"Loaded {len(documents)} chapters from {DATA_PATH}.")
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def save_to_chroma(chunks: list[Document]):
    if os.path.exists(CHROMA_PATH):
        print(
            f"'{CHROMA_PATH}/' already exists — refusing to overwrite it "
            "(rebuilding re-embeds everything and re-bills your OpenAI account).\n"
            f"If you really want to rebuild from scratch, delete the '{CHROMA_PATH}/' "
            "folder yourself and run this script again."
        )
        return

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    total = len(chunks)
    for start in range(0, total, EMBED_BATCH_SIZE):
        batch = chunks[start:start + EMBED_BATCH_SIZE]
        db.add_documents(batch)
        end = min(start + len(batch), total)
        print(f"Embedding chunk {end} of {total}...")

    db.persist()
    sources = {chunk.metadata.get("source") for chunk in chunks}
    print(f"\nIngested {total} chunks from {len(sources)} chapters into '{CHROMA_PATH}/'.")


if __name__ == "__main__":
    main()
