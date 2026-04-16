import os
import tempfile
from pathlib import Path
from backend.ingestion.walker import walk_repo, SUPPORTED_EXTENSIONS

def make_tree(base: Path, files: dict):
    for rel, content in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

def test_collects_supported_files():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        make_tree(base, {
            "src/main.py": "print('hello')",
            "src/util.ts": "export const x = 1",
            "README.md": "# Readme",
            "node_modules/pkg/index.js": "// ignore",
            ".git/config": "[core]",
            "image.png": "binary",
        })
        files = walk_repo(str(base))
        paths = [f["path"] for f in files]
        assert any("main.py" in p for p in paths)
        assert any("util.ts" in p for p in paths)
        assert any("README.md" in p for p in paths)
        assert not any("node_modules" in p for p in paths)
        assert not any(".git" in p for p in paths)
        assert not any("image.png" in p for p in paths)

def test_returns_content_and_language():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "app.py").write_text("def foo(): pass")
        files = walk_repo(str(base))
        assert files[0]["content"] == "def foo(): pass"
        assert files[0]["language"] == "python"
        assert files[0]["path"].endswith("app.py")

def test_skips_large_files():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "big.py").write_text("x" * 600_000)  # >500KB
        files = walk_repo(str(base))
        assert len(files) == 0
