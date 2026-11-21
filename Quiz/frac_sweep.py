"""Replace every vulgar fraction in the quiz files with the plain (a/b) form
CLAUDE.md requires. Form only - this cannot tell whether the code point the
original author chose was the RIGHT fraction, which is the other half of that rule.

  python frac_sweep.py            # dry run: inventory + every rewrite it would make
  python frac_sweep.py --write    # apply
"""
import re, io, os, glob, sys, collections
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"e:\Adhir\AdWinUser\Desktop\icad-dps\ICAD\BooksScanned"
WRITE = "--write" in sys.argv

CHARS = {
    "\u00bd": "1/2", "\u00bc": "1/4", "\u00be": "3/4",
    "\u2150": "1/7", "\u2151": "1/9", "\u2152": "1/10",
    "\u2153": "1/3", "\u2154": "2/3", "\u2155": "1/5", "\u2156": "2/5",
    "\u2157": "3/5", "\u2158": "4/5", "\u2159": "1/6", "\u215a": "5/6",
    "\u215b": "1/8", "\u215c": "3/8", "\u215d": "5/8", "\u215e": "7/8",
}
ENT = {f"&frac{a}{b};": f"{a}/{b}"
       for a, b in [(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5),
                    (4, 5), (1, 6), (5, 6), (1, 7), (1, 8), (3, 8), (5, 8), (7, 8),
                    (1, 9), (1, 10)]}

TOKEN = re.compile("(" + "|".join(map(re.escape, list(CHARS) + list(ENT))) + ")")


def plain(tok):
    return CHARS.get(tok) or ENT[tok]


def rewrite(text):
    """Replace each token with (a/b), but:
      - a token already wrapped in its own parentheses becomes (a/b), not ((a/b))
      - a token straight after a digit (a mixed number like 1 1/2) gets a space,
        so 1(1/2) never appears
    Returns (new_text, list of (before, after) context pairs).
    """
    hits = []
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        tok = m.group(1)
        val = plain(tok)
        before_ctx = text[max(0, m.start() - 48):m.end() + 48]
        lp = text[:m.start()].endswith("(")
        rp = text[m.end():].startswith(")")
        prev = text[m.start() - 1] if m.start() else ""
        if lp and rp:
            out.append(text[pos:m.start() - 1]); repl = f"({val})"; nxt = m.end() + 1
        elif prev.isdigit():
            out.append(text[pos:m.start()]); repl = f" ({val})"; nxt = m.end()
        else:
            out.append(text[pos:m.start()]); repl = f"({val})"; nxt = m.end()
        out.append(repl); pos = nxt
        hits.append((tok, repl, re.sub(r"\s+", " ", before_ctx)))
    out.append(text[pos:])
    return "".join(out), hits


files = sorted(glob.glob(os.path.join(ROOT, "Quiz", "*_Quiz.html"))) + \
        sorted(glob.glob(os.path.join(ROOT, "Quiz", "*", "*_Quiz.html")))

tally, per_file, shown = collections.Counter(), {}, 0
for p in files:
    raw = io.open(p, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    new, hits = rewrite(raw)
    if not hits:
        continue
    per_file[os.path.relpath(p, ROOT)] = len(hits)
    for tok, _, _ in hits:
        tally[tok] += 1
    if WRITE:
        io.open(p, "w", encoding="utf-8", newline="").write(new)
    elif shown < 14:                     # a sample of real rewrites to eyeball
        print(f"\n--- {os.path.relpath(p, ROOT)}  ({len(hits)} hits)")
        for tok, repl, ctx in hits[:3]:
            print(f"    {tok!r} -> {repl!r}")
            print(f"      ...{ctx}...")
        shown += 1

print("\n" + ("APPLIED" if WRITE else "DRY RUN") + f" - {len(per_file)} files, {sum(per_file.values())} replacements")
print("  by token:", "  ".join(f"{k}->{plain(k)}:{v}" for k, v in tally.most_common()))
for f, n in sorted(per_file.items(), key=lambda x: -x[1])[:10]:
    print(f"    {n:5}  {f}")
