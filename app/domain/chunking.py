def chunk_text(content: str, *, max_words: int = 120) -> list[str]:
    words = content.split()
    return [" ".join(words[index : index + max_words]) for index in range(0, len(words), max_words)]
