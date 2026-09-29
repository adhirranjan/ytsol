"""Render one mock set as a PRINTABLE question paper, plus a separate answer key.

    python build_questions.py RT4 1
      -> MockPapers/RT4-Set1-Questions.html   blank answer sheet (page 1) + 75 questions + figures
      -> MockPapers/RT4-Set1-Key.html         the answer key, separate so it need not be printed

Companion to the code-grid <EXAM>-Mock-Sets.html, which stays a pointer sheet.
Question text comes from pool/<LEC>.json, figures from figures/<CODE>.png, and options the
extractor lost from options_*.json (transcribed off the scans and key-checked).
"""
import base64, io, json, os, re, sys, glob, html as H

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MP   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM = (sys.argv[1] if len(sys.argv) > 1 else "RT4").upper()
SETN = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DATE = {"RT4": "12-10-2026", "CAT5": "28-09-2026", "RT3": "21-09-2026"}.get(EXAM, "")
NICE = EXAM.replace("RT", "RT-").replace("CAT", "CAT-")
FIGDIR = os.path.join(MP, "figures")

META = {}
for f in os.listdir(os.path.join(MP, "pool")):
    for r in json.load(open(os.path.join(MP, "pool", f), encoding="utf-8")):
        META[r["code"]] = r

# options the extractor dropped, read back off the scanned pages
OPTS = {}
for f in glob.glob(os.path.join(MP, "options_*.json")):
    for k, v in json.load(open(f, encoding="utf-8")).items():
        if isinstance(v, dict) and v.get("options"): OPTS[k] = v["options"].strip()

# Key letters corrected against the printed options, each verified by derivation.
# M1L1V6Q3: 57d17'45" = 57.295833 deg = 1.000000 rad, so the answer is the 1.00 option, (b).
# The stored answer TEXT ("~ 1 radian") was already right; only the letter was wrong.
KEY_FIX = {"M1L1V6Q3": "b ~ 1 radian",
           # A∩(B−C) = A∩B∩C' = (A∩B)−C, which is option (a); the book keys (b)
           "M2L3V4Q3": "a (A∩B) − C  ⚠ book key says (b) (A−B)∩C",
           # the stored text described the range instead of naming the true statements
           "M4L3V4Q1": "a, c",
           "M1L1V5Q3": "b 42π cm",   # was "132 cm (42π)"; the book prints 42π
           "P3L7V4Q7": "b 30°",   # ⚠ dropped: the key letter was right all along
           # F(t)=6t, motion from t=2.45/6=0.40833 s; v(2)=[3t²−1.96t] over that interval
           # = 8.08 + 0.3001 = 8.38 m/s. No reading of the stem reaches the printed 2.16.
           "P7L1V5Q5": "8.38 m/s  ⚠ book key says 2.16 m/s",
           # the book misprints option (d) as √(3gS)/2; the physics gives √(3gS/2), which is
           # what we print. Letter (d) unchanged.
           "P8L6V3Q5": "d h = S/4 , v = √(3gS/2)  ⚠ book prints option (d) as √(3gS)/2",

           # (c) is false for a FULLY filled subshell: 3up/3down whatever the filling order
           "C2L10V6Q8": "a, b  ⚠ book key says a, b, c"}

# Stem wording corrected against the printed page. Our extracted text for P7L2V5Q4 says the 20 N
# force acts "in the direction of motion", but the book's figure shows v leftward and F rightward,
# i.e. opposing. With the figure now printed beside it the text would contradict the image, so
# defer to the drawing. (The answer, kinetic friction = mu*m*g = 60 N, is unaffected either way.)
STEM_REPLACE = {
 "P7L2V5Q4": [("in the direction of motion", "as shown in the figure")],
 # our option (d) was transcribed as a^(log_a 3), which collapses to just 3; the book prints
 # a^(log_b 3). Verified against the page at 300 dpi.
 "M7L3V5Q8": [("(d) a^(log_a 3)", "(d) a^(log_b 3)")],
 # subscripts lost in extraction - these print as gibberish otherwise
 "C5L5V4Q2": [("SO 3 , CO 3 2− , NO 3 −", "SO3, CO3(2-), NO3(-)")],
 "C1L11V5Q2": [("CH 3 OH", "CH3OH"), ("C 4 H 9 OH", "C4H9OH"), ("CH 3 OCH 3", "CH3OCH3")],
 # the book defines Q once, in C5L4 Level-2 Q1; lifted into a paper the term is unexplained
 "C5L4V2Q2": [("For Q = 3", "For Q = 3 (Q = total number of orbitals)")],
 "C5L4V3Q1": [("What is Q and", "What is Q (total number of orbitals) and")],
 # the figure carries only S1 and S2; there is no scale "S" in this question's diagram
 "P6L6V3Q5": [("(S, S₁, S₂)", "(S₁ and S₂)")],
 # genuinely truncated in the pool - the option list stops mid-way through (b).
 # Remainder transcribed off M8AL1 p07 (book p9); stored key (a) re-derived and correct.
 # superscripts lost in extraction: the book prints x^-4, x^n, x^52
 # the pool stem stops mid-word inside option (d); tail transcribed off C5L5 book p121
 # the book prints the condition as √3|A×B| = A×B, self-contradictory; it means A·B.
 # √3·AB sinθ = AB cosθ → tanθ = 1/√3 → θ = 30°, which is the key letter (b):
 # the stem's "(60°)" and the ⚠ on the answer were both wrong.
 # the book's four choices here are f-vs-theta GRAPHS, not sentences; the prose list our
 # extractor invented is a paraphrase (and stops mid-word). The crop supplies the real ones.
 "P7L1V6Q8": [("is: (a) a curve rising with θ up to 37° (b) a curve rising then falling "
               "before 37° (c) a curve concave upward starting from a non-zero value "
               "(d) an arch that ri", "is:")],
 # truncated mid-option-list; remainder transcribed off the page
 "P7L2V6Q7": [("(a) a-pr, b-ps,",
               "(a) a-pr, b-ps, c-qr, d-qs (b) a-qr, b-pr, c-qr, d-qs "
               "(c) a-pr, b-ps, c-pr, d-st (d) a-ps, b-st, c-qr, d-ps")],
 "P3L7V4Q7": [("the value of θ is: (60°)", "the value of θ is:")],
 # the two turn angles are measured from the line joining the cars - that is what makes the
 # meeting triangle right-angled, and the book prints no figure to show it
 "P4L10V5Q5": [("A turns left at 30°, B turns right at 60°",
                "A turns left at 30° and B turns right at 60°, both measured from the line "
                "joining the cars,")],
 # extraction left a slash-separated digest of the options in the stem; the real labelled
 # list now comes from options_S10_CHEMB.json, so the digest would print twice
 # exponents flattened by extraction - as stored these read as products, not powers
 # both stems stop mid-sentence in the pool; tails transcribed off the printed pages
 "P7L3V5Q4": [("of static and kin",
               "of static and kinetic friction between the block and the surface.")],
 "P8L1V6Q9": [("ii. If block A and plank B are taken as",
               "ii. If block A and plank B are taken as a system, the net work done on the "
               "system in 2 s is 80x J. Find the value of x.")],
 "M8BL3V5Q3": [("2 ax+1 , 2 bx+1 , 2 cx+1", "2^(ax+1), 2^(bx+1), 2^(cx+1)")],
 "P2L5V3Q3": [(" (4 ln x − x + c)", "")],
 "P3L6V4Q1": [(" (p=14/5, q=6/5)", "")],
 "C3L2V6Q8": [(" (electrons / protons / neutrons options)", "")],
 "C3L10V3Q1": [(" (0.05 m / 0.1 m / 0.2 m / 0.3 m)", "")],
 "C3L10V3Q4": [(" (0.02 / 0.1 / 0.2 / 0.15)", "")],
 # the section header got folded into the stem, and the subscripts were lost
 "C5L5V5Q9": [("One or more than one option may be correct: ", ""),
               ("(a) I 3 −", "(a) I3(-)"), ("(b) SF 4", "(b) SF4"),
               ("(c) PF 5", "(c) PF5"), ("(d) IF 5", "(d) IF5")],
 "C5L5V5Q4": [("(d) If bo", "(d) If both assertion and reason are true but reason is not the "
               "correct explanation of assertion.")],
 "M8BL1V5Q5": [("x −4 and x n", "x^(-4) and x^n"), ("If x 52 is", "If x^52 is")],
 "M8AL1V5Q10": [("(b) P→a, Q→c",
                 "(b) P→a, Q→c, R→e, S→b, T→d "
                 "(c) P→c, Q→d, R→b, S→a, T→e "
                 "(d) P→e, Q→a, R→b, S→d, T→c")],
}

# editorial notes the extractor left inside stems - these must never reach a printed paper
EDITORIAL = re.compile(r"\s*\[(?:off-topic|note|sic|unclear|missing|todo)[^\]]*\]", re.I)

# Stems stored as a one-line shorthand where the book prints the real question. Assertion-Reason
# items suffer most: the paraphrase leaves the paper showing an A/R question with no A and no R.
# Text transcribed off the page; the option list is appended separately from options_*.json.
STEM_FULL = {
 "C2L3V4Q10": ("Which of the following statements are correct? "
   "Statement I: Increasing the intensity of incident light increases the number of "
   "photoelectrons emitted per second. "
   "Statement II: Increasing the intensity of light increases the maximum kinetic energy of "
   "emitted photoelectrons. "
   "Statement III: Maximum kinetic energy of photoelectrons depends only on the frequency of "
   "incident light."),
 "C1L10V6Q8": ("Assertion: Surface tension decreases with rise in temperature and becomes zero "
   "at the critical temperature. "
   "Reason: With increase in temperature, cohesive forces between molecules decrease."),
 "M1L1V5Q3": ("A point moves along a circle of radius 7 cm from an initial position P through "
   "an angle θ = π/3 to reach Q. If the point instead traverses θ′ = π/3 + 6π, what is the net "
   "difference in arc lengths measured along the same (positive) direction from P to Q′ and "
   "from P to Q?"),
 "M2L1V5Q1": ("In a group of 500 people, 200 can speak Hindi alone while only 125 can speak "
   "English alone. The number of people who can speak both Hindi and English is"),
 "M4L3V4Q1": ("Let G(x) = {1/x}, the fractional part of 1/x, for x in (0,1]. "
   "Which of the following is/are true? (one or more options may be correct)"),
 "M4L3V4Q4": ("For real x in [0,10), define F(x) = floor({x} + x/3). Which of the following "
   "sets equals the range of F on [0,10)?"),
 "M1L1V5Q4": ("A chord subtends an angle of θ radians at the centre of a circle of radius r. "
   "If the corresponding arc length equals twice the radius (s = 2r), what is θ, and in which "
   "quadrant does its terminal side lie if θ is taken as the principal representative "
   "in (0, 2π)?"),
 "C1L11V4Q9": ("Assertion: H2O has a higher dielectric constant than H2S. "
   "Reason: An extensive hydrogen-bond network in water increases molecular association "
   "and polarity."),
 "C2L1V6Q3": ("Assertion: Cathode rays consist of identical negatively charged particles "
   "irrespective of the nature of the gas or the cathode material used. "
   "Reason: In the discharge tube, any gas taken inside produces electrons that carry the same "
   "charge and mass, proving that electrons are universal constituents of all atoms."),
 "C2L7V4Q9": ("A certain transition in the hydrogen spectrum from an excited state to the ground "
   "state, in one or more steps, gives rise to a total of 10 lines. How many of these belong to "
   "the UV spectrum?"),
 "C2L7V6Q9": ("A hydrogen atom is excited by giving it 8.4 eV of energy. The number of spectral "
   "lines emitted is"),
 "C2L10V6Q8": ("Argon (Z = 18) has fully filled 2p and 3p subshells, filled in accordance with "
   "Hund's rule. Which of the following statements is/are correct?"),
 "C1L7V6Q10": ("Assertion: At a fixed temperature, the difference between the RMS speed and the "
   "average speed of gas molecules decreases as the molar mass of the gas increases. "
   "Reason: Both RMS speed and average speed of gas molecules are directly proportional to the "
   "square root of temperature and inversely proportional to the square root of molar mass."),
 "C2L2V6Q9": ("Assertion: When a black body is heated, it emits radiation only of certain discrete "
   "energies and not a continuous range. "
   "Reason: According to Planck's hypothesis, energy exchange between matter and radiation occurs "
   "in small, indivisible packets called quanta, each having energy equal to hν."),
}

# data printed with the stem that extraction lost entirely; verified against the book page
STEM_ADD = {
 "C1L3V5Q9": " (M_He = 4.00 x 10^-3 kg/mol, R = 8.314 J/mol/K)",
 "C2L11V5Q5": " (one or more options may be correct)",
 "C4L1V6Q3": (" A: 1s2 2s2 2p1 ; B: 1s2 2s2 2p6 3s2 3p1 ; C: 1s2 2s2 2p6 3s2 3p3 ; "
              "D: 1s2 2s2 2p6 3s2 3p5 ; E: 1s2 2s2 2p6 3s2 3p6 4s2."),
}

# PRINTED pointer corrections, from tag_fix.json (produced by the merged-scan audit).
# Our extraction numbers questions within a section, but where the BOOK prints one combined
# exercise set for two lectures (e.g. "P-3 : VECTORS : L-6 & L-7") our splitter filed them as two
# lectures and restarted each count at 1. The drift is per-question, not a fixed offset, so this
# is a lookup. It changes only what is PRINTED - pool/, rankings/, figures/ and the mock sets keep
# using the stable internal code.
_tf = os.path.join(MP, "tag_fix.json")
TAG_FIX = json.load(open(_tf, encoding="utf-8")) if os.path.exists(_tf) else {}
tag = lambda c: TAG_FIX.get(c, c)

h = open(os.path.join(MP, "%s-Mock-Sets.html" % EXAM), encoding="utf-8").read()
card = re.split(r'<div class="setcard" id="s(\d+)">', h)
qpart = dict(zip(card[1::2], card[2::2]))[str(SETN)].split("<details")[0]
SETS = {}
subs = re.split(r'<h3>(Physics|Chemistry|Mathematics)</h3>', qpart)
for j in range(1, len(subs), 2):
    g = re.findall(r'<div class="grid">(.*?)</div>\s*</div>', subs[j + 1], re.S)
    a, b = [re.findall(r'<span class="code">([^<]+)</span>', x) for x in g][:2]
    SETS[subs[j]] = {"A": a, "B": b}

VULGAR = {"¼":"1/4","½":"1/2","¾":"3/4","⅐":"1/7","⅑":"1/9","⅒":"1/10",
          "⅓":"1/3","⅔":"2/3","⅕":"1/5","⅖":"2/5","⅗":"3/5","⅘":"4/5",
          "⅙":"1/6","⅚":"5/6","⅛":"1/8","⅜":"3/8","⅝":"5/8","⅞":"7/8"}
def defrac(t):
    o = []
    for i, c in enumerate(t):
        if c in VULGAR:
            nxt = t[i + 1] if i + 1 < len(t) else ""
            o.append("(%s)" % VULGAR[c] if nxt.isalnum() else VULGAR[c])
        else: o.append(c)
    return "".join(o)

UNITS = {"ms","m","s","j","n","kg","kmh","nm","cm","mol","gmol","mm","ev","rads","ms2","k",
         "atm","l","g","hz","c","a","v","w","pa","deg","kjmol"}
_norm = lambda t: re.sub(r"[^0-9a-z.]", "", t.lower())

def stem(code):
    """Strip a trailing (...) that merely repeats the answer. Require whitespace before it, so a
       glued expression such as f(2) is never mistaken for a leak."""
    s = STEM_FULL.get(code) or defrac(re.sub(r"\s+", " ", META[code].get("stem", "")).strip())
    s = re.sub(r"\*+([^*]+?)\*+", r"\1", s)
    s = EDITORIAL.sub("", s).strip()
    # a bare [12] left at the end is the extractor echoing the answer, not an interval
    s = re.sub(r"\s*\[\s*-?[\d.]+\s*\]\s*$", "", s).strip()
    s = re.sub(r"\s*\[\s*MULTIPLE CORRECT\s*\]", " (one or more options may be correct)", s, flags=re.I)
    s = re.sub(r"\s*[—–]\s*$", "", s).strip()   # stray trailing dash left by extraction
    for old, new in STEM_REPLACE.get(code, []): s = s.replace(old, new)
    m = re.search(r"\s+\(([^()]{1,60})\)\s*$", s)
    if m and not re.search(r"\(a\)", s) and m.group(1).count(" / ") < 2:
        # a trailing "(x / y / z / w)" is a slash-separated OPTION LIST, not a leaked answer -
        # the correct answer naturally appears inside it, which is what fooled this check before
        inner = m.group(1).strip(); i = _norm(inner)
        a = _norm(re.sub(r"^[a-dA-D][\s\).:]+", "", META[code]["answer"].strip()))
        if i and i not in UNITS and (i in a or a in i):
            s = s[:m.start()].rstrip()
            if not s.endswith(("?", ".", ":")): s += "."
    if code in STEM_ADD:
        s = s.rstrip(" .") + "." + STEM_ADD[code]
    if code in OPTS and not re.search(r"\(a\)", s):
        sep = "" if s.rstrip().endswith((":", "?")) else "."
        s = s.rstrip(" .") + sep + " " + OPTS[code]
    return s

def ans(code):
    if code in KEY_FIX: return KEY_FIX[code]
    return defrac(re.sub(r"\s+", " ", META[code]["answer"]).strip()) or "?"

def figure(code, px=700, q=62):
    """small grayscale JPEG - line drawings stay legible under heavy compression"""
    p = os.path.join(FIGDIR, code + ".png")
    if not os.path.exists(p): return ""
    from PIL import Image
    im = Image.open(p).convert("L")
    if im.width > px: im = im.resize((px, round(im.height * px / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True)
    return ('<img class="fig" alt="" src="data:image/jpeg;base64,%s">'
            % base64.b64encode(buf.getvalue()).decode())

CSS = """<style>
*{box-sizing:border-box}
body{font:9.6pt/1.3 Georgia,"Times New Roman",serif;color:#000;background:#fff;margin:0}
.wrap{max-width:200mm;margin:0 auto;padding:6mm 7mm}
h1{font-size:13.5pt;margin:0 0 1mm;text-align:center}
.sub{text-align:center;font-size:8.3pt;margin:0 0 3mm;color:#333}
.ident{display:flex;gap:6mm;font-size:8.6pt;margin:0 0 3mm;border-bottom:1px solid #000;padding-bottom:2mm}
.ident span{flex:1;border-bottom:1px dotted #666}
h2.sec{font-size:10.5pt;margin:4mm 0 1.5mm;padding:1mm 2mm;background:#eee;border-left:3px solid #000}
h3.part{font-size:8.6pt;margin:2.5mm 0 1mm;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:#333}
.qlist{column-count:2;column-gap:7mm}
.q{break-inside:avoid;margin:0 0 2.2mm;display:flex;gap:1.6mm;font-size:9.3pt}
.q .n{font-weight:700;min-width:5.2mm;text-align:right}
.q .b{flex:1;min-width:0}
.fig{display:block;max-width:100%;max-height:42mm;width:auto;height:auto;margin:1mm 0 0}
.tag{font-family:ui-monospace,Consolas,monospace;font-size:6.8pt;color:#666;
     letter-spacing:-.01em;white-space:nowrap}
.sheet{page-break-after:always;break-after:page}
.sheet h1{font-size:16pt;margin:0 0 1.5mm}
.sheet .sub{font-size:9.4pt;margin:0 0 3mm}
.sheet .ident{font-size:10pt;gap:8mm;margin:0 0 4mm;padding-bottom:2.5mm}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:7mm}
.col h4{font-size:11pt;margin:0 0 2mm;text-align:center;background:#000;color:#fff;padding:1.8mm}
.row{display:flex;align-items:center;gap:2.2mm;font-size:9.6pt;padding:1.25mm 0;
     border-bottom:1px dotted #bbb}
.row b{min-width:7mm;text-align:right;font-weight:700}
.bub{width:5.6mm;height:5.6mm;border:.9px solid #000;border-radius:50%;display:inline-block;
     text-align:center;line-height:5.4mm;font-size:7pt;color:#777}
.box{border:.9px solid #000;height:6.6mm;flex:1;max-width:40mm}
.nvt{font-size:8.6pt;color:#333;margin:2.2mm 0 1.2mm;text-align:center;font-style:italic}
.keyrow .row{font-size:8.3pt;padding:.4mm 0}
.tiny{font-size:7pt;color:#666;margin-left:1.2mm;white-space:nowrap}
@media print{.wrap{padding:0}@page{size:A4;margin:9mm}}
</style>"""

def sheet():
    cols = []
    for subj in ("Physics", "Chemistry", "Mathematics"):
        rows = ['<div class="col"><h4>%s</h4>' % subj]
        # a handful of Part A questions are ones the book prints with no choices (more numerical
        # questions fell in this subject than Part B's five slots hold). Give those rows a write-in
        # box rather than bubbles the student cannot use.
        for i in range(1, 21):
            if has_choices(SETS[subj]["A"][i - 1]):
                rows.append('<div class="row"><b>%d</b>%s</div>'
                            % (i, "".join('<span class="bub">%s</span>' % L for L in "abcd")))
            else:
                rows.append('<div class="row"><b>%d</b><span class="box"></span></div>' % i)
        rows.append('<div class="nvt">Numerical &#8212; write the value</div>')
        for i in range(21, 26):
            rows.append('<div class="row"><b>%d</b><span class="box"></span></div>' % i)
        cols.append("".join(rows) + '</div>')
    return ('<div class="sheet"><h1>ICAD %s &#183; Set %d &#8212; Answer Sheet</h1>'
            '<p class="sub">Exam %s &#183; 75 Q &#183; 300 marks &#183; 3 hours &#183; '
            '+4 correct, &#8722;1 wrong, 0 blank</p>'
            '<div class="ident">Name <span></span> Roll No <span></span> Date <span></span></div>'
            '<div class="grid3">%s</div>'
            '<p class="nvt">Bubbles &#8212; single correct &#183; Box &#8212; write the value &#183; each subject out of 100</p></div>' % (NICE, SETN, DATE, "".join(cols)))

# the only question whose four choices ARE the diagram (four graphs labelled a-d)
OPTIONS_IN_FIGURE = {"M4L1V3Q4",   # four graphs labelled a-d
                     "P4L6V4Q1",   # a-t stimulus plus four v-t option plots, one crop
                     "P7L1V6Q8",   # incline plus four f-vs-theta option graphs, one crop
                     "P4L6V6Q5"}   # four y-t curves; stem is only "which curve depicts its motion?"

def has_choices(code):
    """options print as (a)... (b)..., or as slash-separated values, or - for one question -
       they are the cropped figure itself. A scene diagram is NOT a set of options."""
    s = stem(code)
    return bool(re.search(r"\(a\)", s) or s.count(" / ") >= 2 or code in OPTIONS_IN_FIGURE)


def repartition(codes):
    """Part A prints as "single correct" and Part B as "numerical value", but the set builder
       allocated questions by chapter, not by type - leaving option-less questions stranded under
       a single-correct heading. Same 25 questions, re-sorted: the ones the book prints with
       choices fill Part A, the option-less ones fall to Part B."""
    yes = sorted(c for c in codes if has_choices(c))
    no  = sorted(c for c in codes if not has_choices(c))
    # pick Part B by code, not by position, so re-running this on its own output is a no-op
    b = set(no[:5]) | set(yes[:max(0, 5 - len(no))])
    return [c for c in codes if c not in b], [c for c in codes if c in b]

for subj, v in SETS.items():
    a, b = repartition(v["A"] + v["B"])
    SETS[subj] = {"A": a, "B": b}

body, key = [], []
for subj in ("Physics", "Chemistry", "Mathematics"):
    S = SETS[subj]
    body.append('<h2 class="sec">%s</h2>' % subj)
    key.append('<div class="col"><h4>%s</h4>' % subj)
    n = 0
    for part, head in (("A", "Part A &#183; Q1&#8211;20 &#183; single correct"),
                       ("B", "Part B &#183; Q21&#8211;25 &#183; numerical value")):
        body.append('<h3 class="part">%s</h3><div class="qlist">' % head)
        for c in S[part]:
            n += 1
            nv = "" if part == "B" or has_choices(c) else ' <span class="tiny">(write the value)</span>'
            body.append('<div class="q"><div class="n">%d.</div><div class="b">'
                        '<span class="tag">%s</span> %s%s%s</div></div>'
                        % (n, tag(c), H.escape(stem(c)), nv, figure(c)))
            key.append('<div class="row"><b>%d</b> %s <span class="tiny">%s</span></div>'
                       % (n, H.escape(ans(c)), tag(c)))
        body.append('</div>')
    key.append('</div>')

paper = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
         '<title>ICAD %s Set %d</title>' % (NICE, SETN) + CSS +
         '</head><body><div class="wrap">' + sheet() +
         '<h1>ICAD %s &#183; Set %d</h1>' % (NICE, SETN) +
         '<p class="sub">Exam %s &#183; 25 Physics &#183; 25 Chemistry &#183; 25 Mathematics '
         '&#183; 300 marks &#183; 3 hours &#183; +4 / &#8722;1</p>' % DATE +
         "".join(body) + '</div></body></html>')
pq = os.path.join(MP, "%s-Set%d-Questions.html" % (EXAM, SETN))
open(pq, "w", encoding="utf-8").write(paper)

keyhtml = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<title>ICAD %s Set %d Key</title>' % (NICE, SETN) + CSS +
           '</head><body><div class="wrap"><h1>ICAD %s &#183; Set %d &#8212; Answer Key</h1>'
           '<p class="sub">Book key &#8212; re-verify, ICAD keys are ~1-in-14 defective</p>'
           '<div class="grid3 keyrow">%s</div></div></body></html>' % (NICE, SETN, "".join(key)))
pk = os.path.join(MP, "%s-Set%d-Key.html" % (EXAM, SETN))
open(pk, "w", encoding="utf-8").write(keyhtml)

nq = sum(len(v["A"]) + len(v["B"]) for v in SETS.values())
figs = [c for v in SETS.values() for c in v["A"] + v["B"]
        if os.path.exists(os.path.join(FIGDIR, c + ".png"))]
noopt = [c for v in SETS.values() for c in v["A"]          # Part B needs no choices
         if re.match(r"^[a-dA-D][\s\).:]", META[c]["answer"].strip()) and not has_choices(c)]
print("WROTE %-28s %6.0f KB  (%d questions, %d figures)"
      % (os.path.basename(pq), os.path.getsize(pq) / 1024, nq, len(figs)))
print("WROTE %-28s %6.0f KB" % (os.path.basename(pk), os.path.getsize(pk) / 1024))
print("options recovered from scans : %d" % len(OPTS))
print("MCQs printing with no options: %d %s" % (len(noopt), noopt or ""))
