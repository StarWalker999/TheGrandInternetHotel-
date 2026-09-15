"""Portable Hotel Agent v1: small, inspectable coding-tool runtime. No network access."""
import re
import unicodedata

DEFAULT = {"unicode": False, "separators": False, "stable_unique": False, "numeric_sort": False}

def execute(config, task, value):
    if task == "slugify":
        text = str(value).lower().strip()
        if config.get("unicode"):
            text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        if config.get("separators"):
            return re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        return text.replace(" ", "-")
    if task == "unique":
        return list(dict.fromkeys(value)) if config.get("stable_unique") else sorted(set(value))
    if task == "sort_numbers":
        return sorted(value, key=float) if config.get("numeric_sort") else sorted(value, key=str)
    raise ValueError("Unsupported task")

if __name__ == "__main__":
    import json, pathlib, sys
    config = json.loads(pathlib.Path(__file__).with_name("agent.json").read_text())["config"]
    request = json.load(sys.stdin)
    print(json.dumps(execute(config, request["task"], request["input"])))
