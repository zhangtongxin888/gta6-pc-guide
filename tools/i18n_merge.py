"""Merge numbered translation chunks (i18n/_<lang>_N.txt, lines "index|text") into i18n/<lang>.json."""
import glob, json, re, sys
src = json.load(open("i18n/_source.json"))
for lang in sys.argv[1:]:
    tr = {}
    for f in sorted(glob.glob(f"i18n/_{lang}_*.txt")):
        for line in open(f, encoding="utf-8").read().split("\n"):
            if not line.strip():
                continue
            i, _, text = line.partition("|")
            tr[int(i)] = text
    missing = [i for i in range(len(src)) if i not in tr]
    problems = []
    out = {}
    for i, en in enumerate(src):
        if i not in tr:
            continue
        t = tr[i]
        if en.endswith(" ") and not t.endswith(" "):
            t += " "
        if re.findall(r"</?\w+", en) != re.findall(r"</?\w+", t):
            problems.append((i, "tags", en, t))
        if re.findall(r"\{\w+\}", en) != re.findall(r"\{\w+\}", t):
            problems.append((i, "placeholders", en, t))
        out[en] = t
    existing = {}
    try:
        existing = json.load(open(f"i18n/{lang}.json"))
    except FileNotFoundError:
        pass
    existing.update(out)
    json.dump(existing, open(f"i18n/{lang}.json", "w"), ensure_ascii=False, indent=1, sort_keys=True)
    print(lang, "translated", len(out), "missing", missing[:20], "problems", len(problems))
    for p in problems[:10]:
        print("  ", p)
