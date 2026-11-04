/* ============================================================
   ENGINE  v2 — one question at a time · soft per-question timer ·
   downloadable result page.  Identical across chapters.
   ============================================================ */
const BY_ID = {}; QUIZ.forEach(q => BY_ID[q.id] = q);
const LETTERS = ["A","B","C","D","E","F"];
const DEFAULT_T = 90;                       // seconds, for a question with no t
const CH_TITLE = document.querySelector("header.hero h1").textContent.trim();
const CH_TAG   = CH_TITLE.split("·")[0].trim();
const DONE_TITLE = "Chapter " + CH_TAG + " mastered";
const FILE_TAG = (decodeURIComponent(location.pathname.split("/").pop() || "").replace(/\.html?$/i, "") || CH_TAG + "_Quiz").replace(/[^\w-]+/g, "");

let selected = LECTURES.map(l => l.key);   // all lectures on by default
let selIds   = [];                          // ids in the chosen lectures
let round = 0, pool = [], order = {}, picked = {};
let wrongIds = [], leftIds = [], attempts = {}, history = [];
let cur = 0, spent = {}, roundSecs = 0, totalSecs = 0, log = [];
let startedAt = null, autoSaved = false;

function $(id){ return document.getElementById(id); }
function show(scr){
  ["intro","quiz","sub","review","done"].forEach(s => $("scr-"+s).classList.add("hide"));
  $("scr-"+scr).classList.remove("hide");
  window.scrollTo({top:0,behavior:"smooth"});
}
function shuffle(arr){
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function lecName(key){ const l = LECTURES.find(x => x.key === key); return l ? l.name : key; }
function countIn(key){ return QUIZ.filter(q => q.lec === key).length; }
function budget(q){ return q.t || DEFAULT_T; }
function fmt(s){ s = Math.round(s || 0); return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2); }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;"); }

/* ---------- lecture picker ---------- */
function renderPicker(){
  const box = $("lecPicker");
  box.innerHTML = "";
  LECTURES.forEach(l => {
    const on = selected.indexOf(l.key) !== -1;
    const lab = document.createElement("label");
    lab.className = "lecpick" + (on ? " on" : "");
    lab.id = "lp_" + l.key;
    lab.onclick = function(e){ if (e.target.tagName !== "INPUT") { e.preventDefault(); } toggleLecture(l.key); };
    lab.innerHTML = '<input type="checkbox" ' + (on ? "checked" : "") + '>' +
      '<span><span class="nm">' + l.name + '</span><br><span class="ds">' + l.desc + '</span></span>' +
      '<span class="ct">' + countIn(l.key) + ' Q</span>';
    box.appendChild(lab);
  });
  const n = QUIZ.filter(q => selected.indexOf(q.lec) !== -1).length;
  $("selCount").textContent = n + " question" + (n === 1 ? "" : "s") + " selected";
  $("startBtn").disabled = (n === 0);
}
function toggleLecture(key){
  const i = selected.indexOf(key);
  if (i === -1) selected.push(key); else selected.splice(i, 1);
  renderPicker();
}
function setAllLectures(on){
  selected = on ? LECTURES.map(l => l.key) : [];
  renderPicker();
}

/* ---------- rounds ---------- */
function startQuiz(){
  selIds = QUIZ.filter(q => selected.indexOf(q.lec) !== -1).map(q => q.id);
  if (!selIds.length) return;
  round = 0; pool = selIds.slice(); attempts = {}; history = []; log = [];
  totalSecs = 0; startedAt = new Date(); autoSaved = false;
  $("pSel").textContent = selIds.length;
  examStart();
  nextRound();
}
function backToIntro(){
  examStop();
  round = 0; pool = []; picked = {}; order = {}; spent = {};
  wrongIds = []; leftIds = []; attempts = {}; history = []; log = [];
  renderPicker();
  show("intro");
}

function nextRound(){
  round++;
  pool.forEach(id => { attempts[id] = (attempts[id] || 0) + 1; });
  renderPool();
}

function renderPool(){
  picked = {}; order = {}; spent = {}; roundSecs = 0; cur = 0;
  pool.forEach(id => { order[id] = shuffle(BY_ID[id].opts.map((_, k) => k)); });
  $("pRound").textContent = round;
  $("pCount").textContent = pool.length;
  $("pTot").textContent = pool.length;
  $("pMast").textContent = selIds.length - pool.length;
  $("pSel").textContent = selIds.length;
  $("pTime").textContent = "0:00";

  // palette: one button per question, grouped by lecture
  const pal = $("palette");
  pal.innerHTML = "";
  let grp = null, curLec = null;
  pool.forEach((id, i) => {
    const q = BY_ID[id];
    if (q.lec !== curLec){
      curLec = q.lec;
      grp = document.createElement("div"); grp.className = "pgrp";
      grp.innerHTML = '<span class="plab">' + q.lec + '</span>';
      pal.appendChild(grp);
    }
    const b = document.createElement("button");
    b.className = "pb"; b.id = "pb" + id; b.textContent = i + 1;
    b.title = q.blk + " · " + q.topic;
    b.onclick = function(){ showQ(i); };
    grp.appendChild(b);
  });
  showQ(0);
  updateProgress();
  show("quiz");
}

function showQ(i){
  if (i < 0 || i >= pool.length) return;
  cur = i;
  const id = pool[i], q = BY_ID[id];
  let h = '<div class="sechead" style="margin-top:0">' + lecName(q.lec) + '</div>' +
          '<div class="q" id="q' + id + '">' +
          '<div class="qhead"><span class="qnum">Q' + (i + 1) + '</span>' +
          '<span class="qlec">' + q.lec + '</span>' +
          '<span class="qtopic">' + q.blk + ' · ' + q.topic + '</span>';
  if (attempts[id] > 1) h += '<span class="qtopic">· attempt ' + attempts[id] + '</span>';
  h += '<span class="clock" id="clock" title="time on this question / soft budget">0:00 / ' + fmt(budget(q)) + '</span>' +
       '</div><div class="qtext">' + q.q + '</div>';
  order[id].forEach((orig, k) => {
    const on = picked[id] === orig;
    h += '<label class="opt' + (on ? ' picked' : '') + '" id="o' + id + '_' + orig + '" onclick="pick(' + id + ',' + orig + ')">' +
         '<input type="radio" name="q' + id + '"' + (on ? ' checked' : '') + '>' +
         '<span class="lt">' + LETTERS[k] + '.</span>' +
         '<span>' + q.opts[orig] + '</span></label>';
  });
  h += '</div>';
  $("qcard").innerHTML = h;
  $("pCur").textContent = i + 1;
  $("prevBtn").disabled = (i === 0);
  $("nextBtn").disabled = (i === pool.length - 1);
  pool.forEach(x => { const b = $("pb" + x); if (b) b.classList.toggle("cur", x === id); });
  paintClock();
}

function pick(id, orig){
  dirty = true;
  picked[id] = orig;
  BY_ID[id].opts.forEach((_, k) => {
    const el = $("o" + id + "_" + k);
    if (el) el.classList.toggle("picked", k === orig);
  });
  const b = $("pb" + id); if (b) b.classList.add("ans");
  updateProgress();
}

function updateProgress(){
  const n = Object.keys(picked).length, left = pool.length - n;
  $("pAns").textContent = n;
  $("pBar").style.width = (pool.length ? (n / pool.length * 100) : 0) + "%";
  $("submitHint").innerHTML = left
    ? "<b>" + left + "</b> question" + (left === 1 ? "" : "s") + " still unanswered — unanswered counts as wrong and comes back in the next round."
    : "Every question in this round has an answer. Submit to see your score and the review.";
}

/* ---------- soft timer: counts only while the question screen is up ---------- */
function timerOn(){
  return examActive && !examPaused && !$("scr-quiz").classList.contains("hide") && !isAway();
}
function tick(){
  if (!timerOn()) return;
  const id = pool[cur];
  if (id === undefined) return;
  spent[id] = (spent[id] || 0) + 1;
  roundSecs++; totalSecs++;
  $("pTime").textContent = fmt(roundSecs);
  paintClock();
}
function paintClock(){
  const id = pool[cur]; if (id === undefined) return;
  const s = spent[id] || 0, b = budget(BY_ID[id]);
  const c = $("clock"), card = $("q" + id), pb = $("pb" + id);
  if (!c) return;
  c.textContent = fmt(s) + " / " + fmt(b);
  const over = s >= b, warn = !over && s >= 0.75 * b;
  c.classList.toggle("warn", warn); c.classList.toggle("over", over);
  if (card){ card.classList.toggle("warn", warn); card.classList.toggle("over", over); }
  if (pb) pb.classList.toggle("over", over);
}
setInterval(tick, 1000);

document.addEventListener("keydown", e => {
  if ($("scr-quiz").classList.contains("hide") || examPaused) return;
  if (e.key === "ArrowRight"){ showQ(cur + 1); e.preventDefault(); }
  else if (e.key === "ArrowLeft"){ showQ(cur - 1); e.preventDefault(); }
  else if (/^[1-6]$/.test(e.key)){
    const id = pool[cur]; if (id === undefined) return;
    const orig = order[id][+e.key - 1];
    if (orig !== undefined) pick(id, orig);
  }
});

/* ---------- submit → review is compulsory ---------- */
function submitRound(){
  wrongIds = []; leftIds = [];
  let right = 0, slow = 0;
  pool.forEach(id => {
    const q = BY_ID[id], secs = spent[id] || 0, b = budget(q);
    const has = (id in picked), ok = has && picked[id] === q.ans;
    if (!has) leftIds.push(id);
    else if (ok) right++;
    else wrongIds.push(id);
    if (ok && secs > b) slow++;
    log.push({ round: round, id: id, pick: has ? picked[id] : null, ok: ok,
               secs: secs, budget: b, over: secs > b });
  });

  const missed = wrongIds.concat(leftIds);
  history.push({ round: round, asked: pool.length, right: right,
                 wrong: wrongIds.length, left: leftIds.length, secs: roundSecs, slow: slow });
  pool = pool.filter(id => missed.indexOf(id) !== -1);

  if (pool.length === 0){ finish(); return; }

  $("subTitle").textContent = "Round " + round + " submitted";
  $("subScore").textContent = right + " / " + history[history.length - 1].asked + " correct";
  $("subDetail").innerHTML =
    "<b>" + wrongIds.length + "</b> answered wrong · <b>" + leftIds.length + "</b> left blank · " +
    "<b>" + (selIds.length - pool.length) + "/" + selIds.length + "</b> of the selection now mastered.<br>" +
    "Round time <b>" + fmt(roundSecs) + "</b> · <b>" + slow + "</b> correct answer" + (slow === 1 ? "" : "s") +
    " ran over the time budget.";
  $("subBtn").textContent = "Review the " + pool.length + " missed question(s) →";
  show("sub");
}

function showReview(){
  $("rvRound").textContent = round;
  $("rvHead").innerHTML = "Showing the <b>" + wrongIds.length + " wrong</b> and <b>" +
    leftIds.length + " unanswered</b> question(s). For each one: why the correct option is correct, and why every other option is wrong.";
  $("rvBtn").textContent = "Re-quiz these " + pool.length + " question(s) →";

  const list = $("rvlist");
  list.innerHTML = "";

  // correct but over budget — no solutions, just the flag
  const slowOnes = log.filter(e => e.round === round && e.ok && e.over);
  if (slowOnes.length){
    const d = document.createElement("div");
    d.className = "banner";
    let h = '<h2>⏱ Correct, but over time (' + slowOnes.length + ')</h2>' +
            '<div style="font-size:.88rem;color:var(--muted)">Right answer, slow route. Worth a second look at the ⚡ shortcut before the exam.</div>';
    slowOnes.forEach(e => {
      const q = BY_ID[e.id];
      h += '<div class="slowrow"><span class="qlec">' + q.lec + '</span> ' + q.blk + ' · ' + q.topic +
           ' — <span class="tover">' + fmt(e.secs) + '</span> of ' + fmt(e.budget) + '</div>';
    });
    d.innerHTML = h;
    list.appendChild(d);
  }

  wrongIds.concat(leftIds).forEach(id => {
    const q = BY_ID[id];
    const wasLeft = leftIds.indexOf(id) !== -1;
    const secs = spent[id] || 0, b = budget(q);
    const div = document.createElement("div");
    div.className = "rv" + (wasLeft ? " left" : "");
    let h = '<div class="qhead"><span class="tagbad' + (wasLeft ? ' tagleft' : '') + '">' +
            (wasLeft ? 'Left blank' : 'Wrong') + '</span>' +
            '<span class="qlec">' + q.lec + '</span>' +
            '<span class="qtopic">' + q.blk + ' · ' + q.topic + '</span></div>' +
            '<div class="qtext">' + q.q + '</div>' +
            '<div class="yourans">Your answer: <b>' +
            (wasLeft ? "— nothing selected —" : q.opts[picked[id]]) + '</b> · ⏱ ' +
            (secs > b ? '<span class="tover">' + fmt(secs) + '</span>' : fmt(secs)) + ' of ' + fmt(b) + ' budget</div>';
    order[id].forEach((orig, k) => {
      const isAns = (orig === q.ans);
      const isYours = (!wasLeft && picked[id] === orig);
      h += '<div class="orow' + (isAns ? " correct" : (isYours ? " yours" : "")) + '">' +
           '<span class="mark">' + (isAns ? "✓" : (isYours ? "✗" : "·")) + '</span>' +
           '<span class="txt">' + LETTERS[k] + '. ' + q.opts[orig] + '</span>' +
           (isAns ? ' <b style="color:var(--good);font-size:.8rem">CORRECT</b>' : '') +
           (isYours ? ' <b style="color:var(--bad);font-size:.8rem">YOUR PICK</b>' : '') +
           '<span class="why">' + q.why[orig] + '</span></div>';
    });
    h += '<div class="sol"><span class="h">Full working</span>' + q.sol + '</div>';
    div.innerHTML = h;
    list.appendChild(div);
  });
  show("review");
}

function finish(){
  const names = selected.map(k => k).join(", ");
  $("dnTitle").textContent = (selected.length === LECTURES.length)
    ? DONE_TITLE : "Selection mastered";
  $("dnLine").innerHTML = "All <b>" + selIds.length + "</b> question(s) across <b>" + names +
    "</b> answered correctly, in <b>" + round + "</b> round(s) and <b>" + fmt(totalSecs) + "</b>.";
  $("dnHist").innerHTML = historyTable() + '<p style="margin-top:10px">' + summaryLine() +
    (leaveCount ? ' <b style="color:var(--bad)">Left the quiz ' + leaveCount + ' time(s).</b>' : '') +
    '</p><p style="margin-top:6px">A result page has been downloaded for later review — keep it in <b>Quiz/Results/</b>.</p>';
  examStop();
  show("done");
  if (!autoSaved){ autoSaved = true; downloadResult(); }
}

function historyTable(){
  let t = '<table><tr><th>Round</th><th>Asked</th><th>Correct</th><th>Wrong</th><th>Blank</th><th>Time</th><th>Correct but slow</th></tr>';
  history.forEach(h => {
    t += '<tr><td>' + h.round + '</td><td>' + h.asked + '</td><td>' + h.right +
         '</td><td>' + h.wrong + '</td><td>' + h.left + '</td><td>' + fmt(h.secs) + '</td><td>' + h.slow + '</td></tr>';
  });
  return t + '</table>';
}
function summaryLine(){
  const repeats = Object.keys(attempts).filter(k => attempts[k] > 1).length;
  const overAny = selIds.filter(id => log.some(e => e.id === id && e.over)).length;
  return repeats + ' of the ' + selIds.length + ' questions needed more than one attempt; ' +
         overAny + ' went over the time budget at least once.';
}

/* ============================================================
   RESULT PAGE — self-contained HTML, downloaded for later review
   ============================================================ */
function buildResultHTML(){
  const now = new Date();
  const when = now.toLocaleString();
  const done = pool.length === 0 && history.length > 0;
  const lecs = selected.map(k => lecName(k)).join(" · ");
  const idx = {}; selIds.forEach((id, i) => idx[id] = i + 1);
  const byId = {}; log.forEach(e => { (byId[e.id] = byId[e.id] || []).push(e); });

  let h = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
    '<title>' + esc(CH_TAG) + ' Quiz Result · ' + esc(when) + '</title>' +
    '<style>' + document.querySelector("style").textContent +
    '\n.rs table{width:100%;border-collapse:collapse;font-size:.85rem;margin:8px 0}' +
    '.rs th,.rs td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}' +
    '.rs th{background:var(--card2);color:var(--brand2)}' +
    'tr.miss td{background:var(--bad-bg)} tr.slowq td:first-child{box-shadow:inset 4px 0 0 var(--warn)}' +
    '.ok{color:var(--good);font-weight:700}.bad{color:var(--bad);font-weight:700}.ovr{color:var(--warn);font-weight:700}' +
    '.tag{display:inline-block;font-size:.68rem;font-weight:800;border-radius:6px;padding:1px 7px;color:#fff;margin-left:6px}' +
    '</style></head><body><div class="wrap rs">';

  h += '<header class="hero"><p>ICAD · Chapter Mastery Quiz · result sheet</p><h1>' + CH_TITLE + '</h1>' +
       '<p>' + esc(when) + ' · ' + (done ? '🏆 mastered' : '⏳ in progress — ' + pool.length + ' question(s) still open') +
       ' · ' + selIds.length + ' questions · ' + round + ' round(s) · total time ' + fmt(totalSecs) + '</p>' +
       '<p style="font-size:.82rem">Lectures: ' + lecs + '</p></header>';

  h += '<div class="banner"><h2>Rounds</h2>' + historyTable() + '<p style="margin:8px 0 0;font-size:.9rem">' + summaryLine() +
       (leaveCount ? ' Left the quiz ' + leaveCount + ' time(s).' : '') + '</p></div>';

  // per-lecture summary
  h += '<div class="banner"><h2>By lecture</h2><table><tr><th>Lecture</th><th>Q</th><th>Right first time</th><th>Over budget (any round)</th><th>Avg time, 1st attempt</th><th>Total time</th></tr>';
  selected.forEach(k => {
    const ids = selIds.filter(id => BY_ID[id].lec === k);
    if (!ids.length) return;
    let first = 0, over = 0, firstSecs = 0, tot = 0;
    ids.forEach(id => {
      const es = byId[id] || [];
      if (es.length && es[0].ok) first++;
      if (es.some(e => e.over)) over++;
      if (es.length) firstSecs += es[0].secs;
      es.forEach(e => tot += e.secs);
    });
    h += '<tr><td>' + lecName(k) + '</td><td>' + ids.length + '</td><td>' + first + ' / ' + ids.length +
         ' (' + Math.round(100 * first / ids.length) + '%)</td><td>' + over + '</td><td>' +
         fmt(ids.length ? firstSecs / ids.length : 0) + '</td><td>' + fmt(tot) + '</td></tr>';
  });
  h += '</table></div>';

  // per-question table
  h += '<div class="banner"><h2>Every question</h2><table><tr><th>#</th><th>Lecture · topic</th><th>Budget</th><th>Round by round</th><th>Status</th></tr>';
  selIds.forEach(id => {
    const q = BY_ID[id], es = byId[id] || [];
    const missed = es.some(e => !e.ok), slow = es.some(e => e.ok && e.over);
    const cells = es.map(e => 'R' + e.round + ' ' + (e.pick === null ? '<span class="bad">— blank</span>' : (e.ok ? '<span class="ok">✓</span>' : '<span class="bad">✗</span>')) +
                               ' ' + (e.over ? '<span class="ovr">' + fmt(e.secs) + '</span>' : fmt(e.secs))).join(' · ');
    const last = es[es.length - 1];
    const status = !es.length ? 'not reached' : (last.ok ? '<span class="ok">mastered</span>' : '<span class="bad">open</span>');
    h += '<tr class="' + (missed ? 'miss ' : '') + (slow ? 'slowq' : '') + '"><td>' + idx[id] + '</td><td><span class="qlec">' + q.lec +
         '</span> ' + q.blk + ' · ' + q.topic + '</td><td>' + fmt(budget(q)) + '</td><td>' + (cells || '—') + '</td><td>' + status + '</td></tr>';
  });
  h += '</table><p style="font-size:.8rem;color:var(--muted)">Red rows were missed at least once; an amber bar marks a correct answer that ran over its budget.</p></div>';

  // full revision cards for everything missed at least once
  const missedIds = selIds.filter(id => (byId[id] || []).some(e => !e.ok));
  h += '<div class="banner mix"><h2>Revision sheet · ' + missedIds.length + ' question(s) missed at least once</h2>' +
       '<div style="font-size:.9rem">Options are in the book order here. Every option carries its reason, followed by the full working.</div></div>';
  missedIds.forEach(id => {
    const q = BY_ID[id], es = byId[id] || [];
    h += '<div class="rv"><div class="qhead"><span class="qnum">#' + idx[id] + '</span><span class="qlec">' + q.lec + '</span>' +
         '<span class="qtopic">' + q.blk + ' · ' + q.topic + ' · budget ' + fmt(budget(q)) + '</span></div>' +
         '<div class="qtext">' + q.q + '</div>' +
         '<div class="yourans">' + es.map(e => 'Round ' + e.round + ': ' + (e.pick === null ? 'left blank' : (e.ok ? 'correct' : 'wrong')) + ' in ' + fmt(e.secs)).join(' · ') + '</div>';
    q.opts.forEach((o, k) => {
      const isAns = (k === q.ans);
      const yours = es.filter(e => e.pick === k && !e.ok).map(e => 'R' + e.round);
      h += '<div class="orow' + (isAns ? ' correct' : (yours.length ? ' yours' : '')) + '">' +
           '<span class="mark">' + (isAns ? '✓' : (yours.length ? '✗' : '·')) + '</span>' +
           '<span class="txt">' + LETTERS[k] + '. ' + o + '</span>' +
           (isAns ? ' <b style="color:var(--good);font-size:.8rem">CORRECT</b>' : '') +
           (yours.length ? ' <b style="color:var(--bad);font-size:.8rem">YOUR PICK ' + yours.join(', ') + '</b>' : '') +
           '<span class="why">' + q.why[k] + '</span></div>';
    });
    h += '<div class="sol"><span class="h">Full working</span>' + q.sol + '</div></div>';
  });

  h += '<div class="foot">Generated by ' + esc(CH_TAG) + ' mastery quiz · ' + esc(when) +
       ' · started ' + esc(startedAt ? startedAt.toLocaleString() : '—') + '</div></div></body></html>';
  return h;
}

function downloadResult(){
  if (!history.length && !Object.keys(picked).length){ return; }
  const html = buildResultHTML();
  const d = new Date(), p = n => ("0" + n).slice(-2);
  const stamp = d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + "_" + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
  const name = "Result_" + FILE_TAG + "_" + stamp + ".html";   // Result_M8A_Quiz_20261104_183045.html
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
}

