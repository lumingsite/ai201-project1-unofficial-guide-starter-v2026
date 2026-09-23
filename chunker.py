"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# campus_life posts run 178-549 characters and are written as short
# paragraphs — a title line, then one paragraph per fact (what's good, what's
# bad, laundry cost, noise level). Fixed 800-char windows never split any of
# that (fallback_split turns 88 documents into 88 chunks), so a post like
# Morrow House's stays one chunk even though it holds four unrelated facts.
#
# Splitting on blank lines fixes the "chunks too big" problem but creates a
# new "too small" one: the title line alone ("Morrow House — what it's
# actually like") is 10-47 characters and isn't a usable chunk on its own.
# So paragraphs are merged, greedily, in document order, until each chunk
# reaches MIN_CHUNK_CHARS — long enough to read as a complete thought,
# without giving up the paragraph boundaries that separate distinct facts.
MIN_CHUNK_CHARS = 100


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents on paragraph breaks, merging forward until each chunk
    reaches MIN_CHUNK_CHARS. See the module comment above for why.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.strip().split("\n\n") if p.strip()]

        groups: list[list[str]] = []
        buffer: list[str] = []
        buffer_len = 0
        for para in paragraphs:
            buffer.append(para)
            buffer_len += len(para)
            if buffer_len >= MIN_CHUNK_CHARS:
                groups.append(buffer)
                buffer, buffer_len = [], 0
        if buffer:
            if groups:
                groups[-1] = groups[-1] + buffer
            else:
                groups.append(buffer)

        for i, group in enumerate(groups):
            chunks.append(
                Chunk(
                    text="\n\n".join(group),
                    source=doc.source,
                    index=i,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
