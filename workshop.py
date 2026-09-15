"""Workshop has practice examples only. Certification lives in a separate module."""
from runtime import execute

PRACTICE = [
    ("slugify", "Hello World", "hello-world"),
    ("slugify", "Crème Brûlée", "creme-brulee"),
    ("slugify", "  A / B!  ", "a-b"),
    ("unique", [3, 1, 3, 2], [3, 1, 2]),
    ("unique", ["z", "a", "z"], ["z", "a"]),
    ("sort_numbers", [10, 2, 1], [1, 2, 10]),
]

def assess(config):
    rows = []
    for task, value, expected in PRACTICE:
        actual = execute(config, task, value)
        rows.append(dict(task=task, input=value, expected=expected, actual=actual, passed=actual == expected))
    return dict(passed=sum(r["passed"] for r in rows), total=len(rows), cases=rows)

def propose(config):
    """Compare one safe change at a time, using only practice performance."""
    best = dict(config)
    experiments = []
    for flag in ("unicode", "separators", "stable_unique", "numeric_sort"):
        if best.get(flag):
            continue
        candidate = dict(best, **{flag: True})
        before, after = assess(best), assess(candidate)
        accepted = after["passed"] > before["passed"]
        experiments.append(dict(change=flag, before=before["passed"], after=after["passed"], accepted=accepted))
        if accepted:
            best = candidate
    return best, experiments
