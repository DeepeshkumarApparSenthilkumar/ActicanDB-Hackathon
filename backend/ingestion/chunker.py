from enum import StrEnum

WINDOW_TOKENS = 512
OVERLAP = 50

class ChunkType(StrEnum):
    FUNCTION = "function"
    CLASS = "class"
    BLOCK = "block"
    PROSE = "prose"

def _sliding_window(file_path: str, content: str, language: str) -> list[dict]:
    words = content.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + WINDOW_TOKENS, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "file_path": file_path,
            "language": language,
            "content": chunk_text,
            "start_line": 0,
            "end_line": 0,
            "chunk_type": ChunkType.PROSE,
        })
        if end == len(words):
            break
        start = end - OVERLAP
    return chunks

def _ast_chunk_python(file_path: str, content: str) -> list[dict]:
    try:
        import tree_sitter_python as tspython
        from tree_sitter import Language, Parser
        PY_LANGUAGE = Language(tspython.language())
        parser = Parser(PY_LANGUAGE)
    except Exception:
        return []

    tree = parser.parse(content.encode())
    lines = content.splitlines()
    chunks = []

    def walk(node):
        if node.type in ("function_definition", "async_function_definition"):
            start = node.start_point[0]
            end = node.end_point[0]
            chunk_lines = lines[start : end + 1]
            chunks.append({
                "file_path": file_path,
                "language": "python",
                "content": "\n".join(chunk_lines),
                "start_line": start + 1,
                "end_line": end + 1,
                "chunk_type": ChunkType.FUNCTION,
            })
        elif node.type == "class_definition":
            start = node.start_point[0]
            end = node.end_point[0]
            chunk_lines = lines[start : end + 1]
            chunks.append({
                "file_path": file_path,
                "language": "python",
                "content": "\n".join(chunk_lines),
                "start_line": start + 1,
                "end_line": end + 1,
                "chunk_type": ChunkType.CLASS,
            })
        else:
            for child in node.children:
                walk(child)

    walk(tree.root_node)
    return chunks

def _ast_chunk_js(file_path: str, content: str, language: str) -> list[dict]:
    try:
        if language == "typescript":
            import tree_sitter_typescript as ts_lang
            from tree_sitter import Language, Parser
            LANG = Language(ts_lang.language_typescript())
        else:
            import tree_sitter_javascript as ts_lang
            from tree_sitter import Language, Parser
            LANG = Language(ts_lang.language())
        parser = Parser(LANG)
    except Exception:
        return []

    tree = parser.parse(content.encode())
    lines = content.splitlines()
    chunks = []

    FUNC_TYPES = {
        "function_declaration", "arrow_function",
        "method_definition", "function_expression",
    }
    CLASS_TYPES = {"class_declaration", "class_expression"}

    def walk(node):
        if node.type in FUNC_TYPES:
            start = node.start_point[0]
            end = node.end_point[0]
            chunks.append({
                "file_path": file_path,
                "language": language,
                "content": "\n".join(lines[start: end + 1]),
                "start_line": start + 1,
                "end_line": end + 1,
                "chunk_type": ChunkType.FUNCTION,
            })
        elif node.type in CLASS_TYPES:
            start = node.start_point[0]
            end = node.end_point[0]
            chunks.append({
                "file_path": file_path,
                "language": language,
                "content": "\n".join(lines[start: end + 1]),
                "start_line": start + 1,
                "end_line": end + 1,
                "chunk_type": ChunkType.CLASS,
            })
        else:
            for child in node.children:
                walk(child)

    walk(tree.root_node)
    return chunks

def chunk_file(file_path: str, content: str, language: str) -> list[dict]:
    if not content.strip():
        return []
    if language == "python":
        chunks = _ast_chunk_python(file_path, content)
        if chunks:
            return chunks
    elif language in ("javascript", "typescript"):
        chunks = _ast_chunk_js(file_path, content, language)
        if chunks:
            return chunks
    return _sliding_window(file_path, content, language)
