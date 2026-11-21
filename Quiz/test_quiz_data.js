/* Data check for every *_Quiz.html under Quiz/ (set folders included).
   Run: node Quiz/test_quiz_data.js            (all files, failures only)
        node Quiz/test_quiz_data.js -v         (also print a per-file line)

   Companion to test_exam_lock.js, which checks behaviour. This one checks the
   question bank itself: that QUIZ/LECTURES still parse, that every row is
   well-formed, and that no vulgar fraction has crept back in.

   The vulgar-fraction rule (CLAUDE.md): write plain (1/2), never the ½ character
   or the &frac12; entity - agents pick the wrong code point for these, so ⅞ has
   been written where 2/5 was meant. Note this checks FORM only; it cannot tell
   whether a plain fraction carries the right value. */
const fs = require("fs"), path = require("path");

const verbose = process.argv.includes("-v");
const QUIZ_DIR = path.join(__dirname);

const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? walk(path.join(d, e.name))
                  : (/_Quiz\.html$/.test(e.name) ? [path.join(d, e.name)] : []));

/** Slice `const NAME = [ ... ]` out of the page, respecting strings and nesting. */
function grab(text, name) {
  const i = text.indexOf("const " + name + " = [");
  if (i < 0) throw new Error("no " + name + " array");
  let j = text.indexOf("[", i), depth = 0, instr = false, esc = false, k = j;
  for (; k < text.length; k++) {
    const c = text[k];
    if (instr) {
      if (esc) esc = false;
      else if (c === "\\") esc = true;
      else if (c === '"') instr = false;
    } else if (c === '"') instr = true;
    else if (c === "[") depth++;
    else if (c === "]") { depth--; if (depth === 0) break; }
  }
  return text.slice(j, k + 1);
}

const VULGAR_CHAR = /[½¼¾⅐-⅞]/;
const VULGAR_ENT  = /&frac\d+;/;
const DOUBLE_PAREN = /\(\(\d+\/\d+\)\)/;   // what a careless ½ -> (1/2) sweep leaves behind

let files = 0, questions = 0, failed = 0;
for (const p of walk(QUIZ_DIR)) {
  const rel = path.relative(QUIZ_DIR, p).split(path.sep).join("/");
  const text = fs.readFileSync(p, "utf8");
  files++;
  const errs = [];
  let Q = [], L = [];
  try {
    Q = eval(grab(text, "QUIZ"));
    L = eval(grab(text, "LECTURES"));
  } catch (e) {
    console.log("FAIL " + rel + "  " + e.message);
    failed++;
    continue;
  }
  questions += Q.length;
  const keys = new Set(L.map(x => x.key));
  const stems = new Set();
  for (const q of Q) {
    const all = [q.q, ...(q.opts || []), q.sol || "", ...(q.why || [])].join(" ");
    if (!keys.has(q.lec)) errs.push(`q${q.id}: lec "${q.lec}" not in LECTURES`);
    if (!Array.isArray(q.opts) || q.opts.length < 2) errs.push(`q${q.id}: opts`);
    else {
      if (!(q.ans >= 0 && q.ans < q.opts.length)) errs.push(`q${q.id}: ans out of range`);
      if (!Array.isArray(q.why) || q.why.length !== q.opts.length)
        errs.push(`q${q.id}: why/opts length mismatch`);
    }
    if (!q.q) errs.push(`q${q.id}: empty stem`);
    if (VULGAR_CHAR.test(all)) errs.push(`q${q.id}: vulgar-fraction character`);
    if (VULGAR_ENT.test(all)) errs.push(`q${q.id}: &fracN; entity`);
    if (DOUBLE_PAREN.test(all)) errs.push(`q${q.id}: ((a/b)) double parens`);
    // A repeated stem is only a fault when the options repeat too. M12 q78/q80 both
    // ask "The in-radius r can be written as" with different identities on offer -
    // legitimate, and told apart on screen by their blk labels.
    const k = ((q.q || "") + "\u0000" + (q.opts || []).join("\u0000")).replace(/\s+/g, "");
    if (stems.has(k)) errs.push(`q${q.id}: duplicate question (same stem AND options)`);
    stems.add(k);
  }
  if (errs.length) {
    failed++;
    console.log("FAIL " + rel);
    [...new Set(errs)].slice(0, 6).forEach(e => console.log("        " + e));
    if (errs.length > 6) console.log(`        ... and ${errs.length - 6} more`);
  } else if (verbose) {
    console.log("ok   " + rel.padEnd(30) + Q.length + " Q, " + L.length + " units");
  }
}

console.log(`\n${files} quiz files, ${questions} questions - ` +
            (failed ? failed + " FAILED" : "all passed"));
process.exit(failed ? 1 : 0);
