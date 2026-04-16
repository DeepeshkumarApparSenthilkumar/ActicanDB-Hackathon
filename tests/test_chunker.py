from backend.ingestion.chunker import chunk_file, ChunkType

PYTHON_CODE = """\
def add(a, b):
    return a + b

class Calculator:
    def multiply(self, a, b):
        return a * b
"""

def test_python_extracts_functions_and_classes():
    chunks = chunk_file("test.py", PYTHON_CODE, "python")
    types = {c["chunk_type"] for c in chunks}
    assert ChunkType.FUNCTION in types or ChunkType.CLASS in types

def test_python_has_line_numbers():
    chunks = chunk_file("test.py", PYTHON_CODE, "python")
    for chunk in chunks:
        assert "start_line" in chunk
        assert "end_line" in chunk
        assert chunk["end_line"] >= chunk["start_line"]

def test_python_has_metadata():
    chunks = chunk_file("test.py", PYTHON_CODE, "python")
    for chunk in chunks:
        assert chunk["file_path"] == "test.py"
        assert chunk["language"] == "python"
        assert chunk["content"].strip()

def test_markdown_uses_sliding_window():
    long_md = "word " * 1000
    chunks = chunk_file("README.md", long_md, "markdown")
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["chunk_type"] == ChunkType.PROSE

def test_unsupported_lang_uses_sliding_window():
    chunks = chunk_file("config.go", "package main\n\nfunc main() {}\n", "go")
    assert len(chunks) >= 1
