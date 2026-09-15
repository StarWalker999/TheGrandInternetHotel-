"""Independent held-out fixtures. Workshop cannot select changes using these results."""
from runtime import execute

BENCHMARK = "hotel-coding-tools/1.0"
HELD_OUT = [
    ("slugify", "Déjà Vu", "deja-vu"), ("slugify", "a___b...c", "a-b-c"),
    ("slugify", "---Welcome!---", "welcome"), ("slugify", "", ""),
    ("slugify", "Room 42", "room-42"), ("slugify", "naïve café", "naive-cafe"),
    ("unique", [4, 2, 4, 1, 2], [4, 2, 1]), ("unique", [], []),
    ("unique", ["b", "A", "b"], ["b", "A"]),
    ("sort_numbers", [20, 3, -2, 0], [-2, 0, 3, 20]),
    ("sort_numbers", [1.5, 1.05, 10, 2], [1.05, 1.5, 2, 10]),
    ("sort_numbers", [], []),
]

def verify(before, after):
    cases = []
    for i, (task, value, expected) in enumerate(HELD_OUT):
        a, b = execute(before, task, value), execute(after, task, value)
        cases.append(dict(id=f"H{i+1:02}", task=task, baseline=a == expected, passed=b == expected,
                          input=value, expected=expected, actual=b))
    return dict(benchmark=BENCHMARK, before=sum(x["baseline"] for x in cases),
                after=sum(x["passed"] for x in cases), total=len(cases),
                regressions=sum(x["baseline"] and not x["passed"] for x in cases), cases=cases)
