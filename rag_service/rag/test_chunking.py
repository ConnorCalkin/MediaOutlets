from rag.chunking import chunk_text


def test_chunking_creates_multiple_chunks():
    text = "This is a test. " * 1000
    chunks = chunk_text(text)

    assert len(chunks) > 1


def test_chunking_handles_empty_input():
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_overlap():
    text = "A" * 4000
    chunks = chunk_text(text, chunk_size=2000, overlap=500)

    assert len(chunks) >= 2
    # check overlap exists
    assert chunks[0][-500:] == chunks[1][:500]
