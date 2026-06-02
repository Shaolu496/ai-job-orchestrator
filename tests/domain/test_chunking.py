from app.domain.chunking import chunk_text


def test_chunk_text_splits_by_word_count():
    chunks = chunk_text("one two three four five six", max_words=3)

    assert chunks == ["one two three", "four five six"]


def test_chunk_text_removes_empty_whitespace():
    chunks = chunk_text("  one   two\n\nthree  ", max_words=2)

    assert chunks == ["one two", "three"]
