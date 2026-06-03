import os
from pathlib import Path

root = Path(".")
exts = {".md", ".txt", ".rst", ".py", ".sh", ".ps1", ".bat", ".c", ".cpp", ".h", ".php", ".js", ".json", ".yaml", ".yml", ".conf", ".ini"}
skip_dirs = {".git", ".github", "node_modules", "__pycache__", ".venv", "venv"}

for path in sorted(root.rglob("*")):
    if path.is_dir():
        continue
    if any(part in skip_dirs for part in path.parts):
        continue
    if path.suffix.lower() in exts or path.name.lower() in {"readme", "license"}:
        print(f"\n<!-- SOURCE: {path.as_posix()} -->\n")
        try:
            print(path.read_text(errors="replace"))
        except Exception as e:
            print(f"[ERROR READING FILE: {e}]")
