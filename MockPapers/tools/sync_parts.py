"""Re-sort each subject's Part A / Part B in <EXAM>-Mock-Sets.html the same way the printed
paper does: questions the book prints with choices go to Part A, option-less ones to Part B.

The set builder allocated by chapter, not by question type, so both parts had drifted from their
own headings - Part A held questions with no printed choices, Part B held ordinary MCQs. Same 25
questions per subject either way; only which part they sit in moves. Each setcard holds 12 grids
in a fixed order - six question grids (Physics A, Physics B, Chemistry A, ... ) then the six
answer-key grids mirroring them - so a subject's four grids are 2i, 2i+1, 6+2i, 7+2i.

    python tools/sync_parts.py RT4
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM = (sys.argv[1] if len(sys.argv) > 1 else "RT4").upper()

# reuse the builder's own stem()/has_choices() so the two files can never disagree
bq = os.path.join(MP, "tools", "build_questions.py")
g = {"__file__": bq}
sys.argv = ["b", EXAM, "1"]
exec(compile(io.open(bq, encoding="utf-8").read().split("\nfor subj, v in SETS.items():")[0],
             "b", "exec"), g)
repartition = g["repartition"]

# the grid's own </div> and its last cell's </div> are adjacent, so anchor on whole cells
GRID = re.compile(r'(?<=<div class="grid">)(?:<div class="cell">.*?</div>)+', re.S)
CELL = re.compile(r'<div class="cell"><span class="n">\d+</span>'
                  r'<span class="code">([^<]+)</span>(.*?)</div>', re.S)
moved = 0

def resort(card):
    global moved
    grids = [(m.start(), m.end(), CELL.findall(m.group(0))) for m in GRID.finditer(card)]
    if len(grids) != 12 or any(len(c) not in (20, 5) for _, _, c in grids):
        raise SystemExit("unexpected setcard shape: %d grids" % len(grids))
    out = []
    for i in range(3):                                  # three subjects
        a, b = repartition([c for _, _, cs in (grids[2 * i], grids[2 * i + 1]) for c, _ in cs])
        moved += sum(1 for x, y in zip([c for c, _ in grids[2 * i][2] + grids[2 * i + 1][2]], a + b)
                     if x != y)
        for q, k in ((2 * i, 6 + 2 * i), (2 * i + 1, 7 + 2 * i)):
            want, start = (a, 1) if len(grids[q][2]) == 20 else (b, 21)
            for j in (q, k):                            # question grid and its answer-key twin
                own = dict(grids[j][2])
                own.update(dict(grids[j - 1 if j % 2 else j + 1][2]))   # the subject's other part
                out.append((grids[j][0], grids[j][1],
                            "".join('<div class="cell"><span class="n">%d</span>'
                                    '<span class="code">%s</span>%s</div>' % (n, c, own[c])
                                    for n, c in enumerate(want, start))))
    for s, e, new in sorted(out, reverse=True):
        card = card[:s] + new + card[e:]
    return card

path = os.path.join(MP, "%s-Mock-Sets.html" % EXAM)
h = re.sub(r'<div class="setcard".*?(?=<div class="setcard"|$)',
           lambda m: resort(m.group(0)), io.open(path, encoding="utf-8").read(), flags=re.S)
io.open(path, "w", encoding="utf-8").write(h)
print("%s: %d cells re-ordered" % (os.path.basename(path), moved))
