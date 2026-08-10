from app.rag.chunker import chunk_text
from app.rag.text_cleaner import clean_text


def test_chunk_count_and_order():
    paragraphs = "\n\n".join(f"Paragraph {i} containing some words." for i in range(50))
    chunks = chunk_text(paragraphs)
    assert len(chunks) > 1
    indexes = [c.index for c in chunks]
    assert indexes == sorted(indexes)
    assert indexes == list(range(len(chunks)))


def test_chunks_respect_size_bound():
    text = ("word " * 500) * 10
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert all(len(c.text) <= 300 for c in chunks)
    assert clean_text(text).startswith(chunks[0].text.rstrip())


def test_overlap_preserves_context():
    text = ("".join(f"token{i} " for i in range(1, 400)))
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    second_start = chunks[1].text[:20]
    assert second_start in text


def test_short_text_single_chunk():
    chunks = chunk_text("hello world")
    assert len(chunks) == 1
    assert chunks[0].char_count == len("hello world")


def test_empty_text_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n ") == []


def test_char_count_matches():
    chunks = chunk_text("The quick brown fox.")
    assert chunks[0].char_count == len("The quick brown fox.")