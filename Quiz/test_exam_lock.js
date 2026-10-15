/* Exam-lock regression check for every <Ch>_Quiz.html in this folder.
   Run: node Quiz/test_exam_lock.js            (all chapters, one line each)
        node Quiz/test_exam_lock.js P7         (one chapter, every check listed)
   Extracts the real EXAM LOCK block from each shipped file and drives it against
   DOM + timer stubs, so it fails if the grace window or strike ladder breaks. */
const fs = require("fs"), assert = require("assert"), path = require("path");

const only  = process.argv[2];
const files = fs.readdirSync(__dirname).filter(f => /_Quiz\.html$/.test(f))
                .filter(f => !only || f === only + "_Quiz.html" || f === only);
if (!files.length) { console.error("no quiz files matched " + only); process.exit(1); }

function mkEl(cls) {
  const s = new Set(cls || []);
  return { classList: { add: c => s.add(c), remove: c => s.delete(c), contains: c => s.has(c) },
           textContent: "", innerHTML: "" };
}

function harness(src) {
  const els = { lockOverlay: mkEl(["hide"]), lockIcon: mkEl(), lockTitle: mkEl(),
                lockMsg: mkEl(), lockSub: mkEl(), "scr-quiz": mkEl() };   // scr-quiz visible
  const h = {}, on = (k, f) => (h[k] = h[k] || []).push(f);
  let focused = true;
  const doc = { addEventListener: on, hidden: false, fullscreenElement: null,
                hasFocus: () => focused,
                exitFullscreen: () => Promise.resolve(),
                documentElement: { requestFullscreen: () => Promise.resolve() } };
  let now = 0, seq = 1, renders = 0;
  const timers = new Map();
  const advance = ms => {
    now += ms;
    [...timers.entries()].filter(t => t[1].at <= now).sort((a, b) => a[1].at - b[1].at)
      .forEach(t => { timers.delete(t[0]); t[1].fn(); });
  };
  const tail = "\nreturn {examStart:examStart,examStop:examStop,resumeQuiz:resumeQuiz," +
    "state:function(){return {examActive:examActive,examPaused:examPaused,strikes:strikes," +
    "leaveCount:leaveCount,dirty:dirty,pending:!!pendingLeave};}," +
    "setDirty:function(v){dirty=v;}};";
  const api = new Function("$", "document", "window", "setTimeout", "clearTimeout", "renderPool",
    src + tail
  )(id => els[id] || mkEl(), doc, { addEventListener: on },
    (fn, ms) => { const id = seq++; timers.set(id, { fn: fn, at: now + ms }); return id; },
    id => timers.delete(id), () => { renders++; });

  const fire = k => (h[k] || []).forEach(f => f());
  return { api: api, els: els, advance: advance, renders: () => renders,
           beforeunload: e => (h.beforeunload || []).forEach(f => f(e)),
           // Alt-Tab to another APP: the tab stays visible, it just loses focus
           away: () => { focused = false; fire("blur"); },
           // switch to another TAB / minimise: the page is actually hidden too
           hide: () => { focused = false; doc.hidden = true; fire("blur"); fire("visibilitychange"); },
           back: () => { focused = true; doc.hidden = false; fire("focus"); fire("visibilitychange"); },
           // a visibilitychange that arrives while they are still away (hidden === false)
           spuriousVisibility: () => fire("visibilitychange") };
}

function suite(src, GRACE) {
  const T = {};

  T["quiz data still parses"] = html => {
    const L = html.match(/const LECTURES = \[[\s\S]*?\n\];/)[0].replace("const", "var");
    const Q = html.match(/const QUIZ = \[[\s\S]*?\n\];/)[0].replace("const", "var");
    const g = {};
    new Function("g", L + Q + ";g.L=LECTURES;g.Q=QUIZ;")(g);
    assert.ok(g.Q.length > 0, "no questions");
    const keys = new Set(g.L.map(l => l.key));
    g.Q.forEach(q => {
      assert.ok(keys.has(q.lec), "orphan unit " + q.lec);
      assert.ok(q.opts.length === 4 && q.why.length === 4, "bad shape at q" + q.id);
      assert.ok(q.ans >= 0 && q.ans < 4, "bad ans at q" + q.id);
    });
  };

  T["a quick glance away is never scored"] = () => {
    const H = harness(src); H.api.examStart();
    H.away(); H.advance(GRACE - 500); H.back(); H.advance(GRACE * 3);
    assert.strictEqual(H.api.state().leaveCount, 0, "scored a leave shorter than the grace window");
    assert.strictEqual(H.api.state().examPaused, false, "paused the quiz over a blip");
  };

  T["staying away past the grace scores exactly one strike"] = () => {
    const H = harness(src); H.api.examStart();
    H.away();
    assert.strictEqual(H.api.state().leaveCount, 0, "scored before the grace elapsed");
    H.advance(GRACE);
    assert.strictEqual(H.api.state().leaveCount, 1, "one Alt-Tab did not score exactly once");
    assert.strictEqual(H.api.state().examPaused, true, "quiz did not pause");
  };

  // regression: a stray visibilitychange used to cancel an in-flight strike, because
  // the handler read document.hidden (still false on an Alt-Tab) as "they are back"
  T["a stray visibilitychange does not excuse a leave"] = () => {
    const H = harness(src); H.api.examStart();
    H.away();                      // tab still visible, just unfocused
    H.advance(1000);
    H.spuriousVisibility();        // fires with hidden === false
    H.advance(GRACE);
    assert.strictEqual(H.api.state().leaveCount, 1, "a stray visibilitychange cancelled a real leave");
  };

  T["switching to another tab is caught too"] = () => {
    const H = harness(src); H.api.examStart();
    H.hide(); H.advance(GRACE);
    assert.strictEqual(H.api.state().leaveCount, 1, "a real tab switch was not caught");
  };

  T["first strike warns but does NOT clear the round"] = () => {
    const H = harness(src); H.api.examStart();
    H.away(); H.advance(GRACE);
    assert.strictEqual(H.renders(), 0, "round was wiped on the first strike");
    assert.ok(/Leave again/.test(H.els.lockMsg.innerHTML), "warning text missing");
    assert.ok(!/restarted/.test(H.els.lockTitle.textContent), "threatened restart too early");
  };

  T["leaving again while paused does not stack strikes"] = () => {
    const H = harness(src); H.api.examStart();
    H.away(); H.advance(GRACE); H.away(); H.advance(GRACE * 2);
    assert.strictEqual(H.api.state().leaveCount, 1, "scored while already paused");
  };

  T["second real leave clears the round"] = () => {
    const H = harness(src); H.api.examStart();
    H.away(); H.advance(GRACE); H.back(); H.api.resumeQuiz();
    H.away(); H.advance(GRACE);
    assert.strictEqual(H.api.state().leaveCount, 2);
    assert.strictEqual(H.renders(), 1, "round was NOT re-rendered");
    assert.ok(/restarted/.test(H.els.lockTitle.textContent), "restart not announced");
  };

  T["every later leave also clears the round"] = () => {
    const H = harness(src); H.api.examStart();
    for (let i = 0; i < 3; i++) { H.away(); H.advance(GRACE); H.back(); H.api.resumeQuiz(); }
    assert.strictEqual(H.renders(), 2, "a later leave got a free pass");
  };

  T["resuming cancels any timer still in flight"] = () => {
    const H = harness(src); H.api.examStart();
    H.away(); H.advance(GRACE); H.back(); H.api.resumeQuiz();
    assert.strictEqual(H.api.state().pending, false, "left a timer armed after resume");
  };

  T["stopping disarms it"] = () => {
    const H = harness(src); H.api.examStart(); H.api.examStop();
    H.away(); H.advance(GRACE * 3);
    assert.strictEqual(H.api.state().leaveCount, 0, "counted a leave after the quiz ended");
    assert.strictEqual(H.api.state().pending, false, "left a timer armed after stop");
  };

  T["beforeunload only guards once answering has begun"] = () => {
    const H = harness(src); H.api.examStart();
    const ev = () => ({ returnValue: null, preventDefault: function () { this.pd = true; } });
    let e = ev(); H.beforeunload(e);
    assert.strictEqual(e.returnValue, null, "prompted before any answer was given");
    H.api.setDirty(true);
    e = ev(); H.beforeunload(e);
    assert.strictEqual(e.returnValue, "", "did not prompt after answering");
  };

  T["review screen never has its answers cleared"] = () => {
    const H = harness(src); H.api.examStart();
    H.els["scr-quiz"].classList.add("hide");          // on the review screen
    H.away(); H.advance(GRACE); H.back(); H.api.resumeQuiz();
    H.away(); H.advance(GRACE);
    assert.strictEqual(H.renders(), 0, "wiped a round while the user was mid-review");
    assert.strictEqual(H.api.state().leaveCount, 2, "leave stopped being counted");
  };

  return T;
}

const MARK = "/* ============================================================\n   EXAM LOCK";
let totalFail = 0;
const graces = new Set();

files.sort().forEach(f => {
  const html = fs.readFileSync(path.join(__dirname, f), "utf8");
  const i = html.indexOf(MARK), j = html.indexOf("renderPicker();\n</script>");
  if (i < 0 || j < 0) { console.log("  MISSING LOCK  " + f); totalFail++; return; }
  const src = html.slice(i, j);
  const GRACE = +src.match(/LEAVE_GRACE_MS = (\d+)/)[1];
  graces.add(GRACE);

  const T = suite(src, GRACE);
  const fails = [];
  Object.keys(T).forEach(name => {
    try { T[name](html); if (files.length === 1) console.log("  ok  " + name); }
    catch (e) { fails.push(name + " - " + e.message); }
  });
  totalFail += fails.length;
  if (files.length > 1) {
    console.log((fails.length ? "  FAIL " : "  ok   ") + f.replace("_Quiz.html", "").padEnd(5) +
                " (" + Object.keys(T).length + " checks, grace " + GRACE + "ms)");
  }
  fails.forEach(x => console.log("        " + x));
});

console.log("\n" + files.length + " chapter(s), grace " + [...graces].join("/") + "ms - " +
            (totalFail ? totalFail + " FAILED" : "all passed"));
process.exit(totalFail ? 1 : 0);
