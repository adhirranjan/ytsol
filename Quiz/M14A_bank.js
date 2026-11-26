const META = {code:"M-14A", name:"The Straight Line", lecRange:"L-1 to L-6", hasSB:false};

const LECTURES = [
  {key:"L-1", name:"L-1 · Inclination, Slope, Intercepts & Equations of the Axes",
   desc:"inclination θ, slope m = tanθ, slope from two points, intercepts on the axes, equations of the axes and lines parallel to them, reading the sign of the slope"},
  {key:"L-2", name:"L-2 · Equation of a Line — Two-Point, Point-Slope, Slope-Intercept & Intercept Forms",
   desc:"the four standard templates, choosing a form from the data, equal intercepts and equal-and-opposite intercepts"},
  {key:"L-3", name:"L-3 · Normal, Parametric & General Forms; Intersection & Concurrency",
   desc:"normal form x cosα + y sinα = p, parametric/distance form, reducing Ax+By+C=0, point of intersection, concurrency determinant"},
  {key:"L-4", name:"L-4 · Angle Between Lines, Parallel/Perpendicular, Distance, Foot & Image",
   desc:"angle between two lines, parallel & perpendicular conditions, line at a given angle, perpendicular distance, distance between parallels, side of a point, foot & image"},
  {key:"L-5", name:"L-5 · Family of Straight Lines & Area of a Parallelogram",
   desc:"L₁ + λL₂ = 0 through a fixed point, fixing λ from a condition, area of the parallelogram made by four lines"},
  {key:"L-6", name:"L-6 · Angle Bisectors (Acute/Obtuse, Origin) & Centres by Slopes",
   desc:"the two bisectors, picking acute vs obtuse, the origin-containing bisector, circumcentre & orthocentre by perpendicular slopes"}
];

/* ============================================================
   QUESTION BANK — ans = index into opts (before shuffling)
   Timer t is computed at load from the spec rule (see bottom).
   ============================================================ */
const QUIZ = [

/* ---------------- L-1 ---------------- */
{id:1, lec:"L-1", blk:"Inclination of a line", topic:"Definition of inclination",
 q:"The inclination of a line is defined as the angle it makes with the",
 opts:[
  "positive direction of the x-axis, measured anticlockwise",
  "positive direction of the y-axis, measured clockwise",
  "nearest coordinate axis",
  "line y = x, measured anticlockwise"],
 ans:0,
 why:[
  "Correct. Inclination θ is measured from the <b>+x-axis</b>, anticlockwise taken positive, so 0° ≤ θ < 180°.",
  "The reference is the x-axis, not the y-axis, and anticlockwise (not clockwise) is the positive sense.",
  "It is always measured from the fixed +x-axis, never from whichever axis happens to be nearer.",
  "The reference line is the x-axis; y = x itself has inclination 45°, it is not the reference."],
 sol:"<b>Inclination</b> θ is the angle a line makes with the <b>positive x-axis</b>, measured anticlockwise (positive). A line parallel to the x-axis has θ = 0°; one parallel to the y-axis has θ = 90°."},

{id:2, lec:"L-1", blk:"Slope (gradient)", topic:"Slope from two points",
 q:"The slope of the line through (2, 3) and (4, 5) is",
 opts:["1", "2", "1/2", "−1"],
 ans:0,
 why:[
  "Correct. m = (5 − 3)/(4 − 2) = 2/2 = <b>1</b>, so the line is inclined at 45°.",
  "This takes only the numerator 5 − 3 = 2 and forgets to divide by the run 4 − 2 = 2.",
  "This inverts the ratio — (4 − 2)/(5 − 3) is the reciprocal, not the slope.",
  "The rise and run are both positive, so the slope is +1, not −1."],
 sol:"m = (y₂ − y₁)/(x₂ − x₁) = (5 − 3)/(4 − 2) = 2/2 = <b>1</b>."},

{id:3, lec:"L-1", blk:"Slope (gradient)", topic:"Slope from inclination",
 q:"A line has inclination 135° with the positive x-axis. Its slope is",
 opts:["−1", "1", "undefined", "0"],
 ans:0,
 why:[
  "Correct. m = tan135° = −tan45° = <b>−1</b>; the line falls left-to-right.",
  "tan135° is negative; +1 would be tan45°, a rising line.",
  "The slope is undefined only at 90° (a vertical line); 135° has a finite tangent.",
  "Slope 0 is tan0° (horizontal); 135° is neither horizontal nor vertical."],
 sol:"m = tanθ = tan135° = tan(180° − 45°) = −tan45° = <b>−1</b>. A negative slope means the line slopes down to the right."},

{id:4, lec:"L-1", blk:"Slope (gradient)", topic:"Slope through negative-coordinate points",
 q:"The slope of the line joining (−1, 2) and (3, −6) is",
 opts:["−2", "2", "−1/2", "−8"],
 ans:0,
 why:[
  "Correct. m = (−6 − 2)/(3 − (−1)) = −8/4 = <b>−2</b>.",
  "The sign is lost — the rise −6 − 2 = −8 is negative, so the slope is negative.",
  "This is the negative reciprocal; it would be the slope of a perpendicular line, not this one.",
  "This is the rise −8 alone, not divided by the run 4."],
 sol:"m = (y₂ − y₁)/(x₂ − x₁) = (−6 − 2)/(3 − (−1)) = −8/4 = <b>−2</b>."},

{id:5, lec:"L-1", blk:"Slope of special lines", topic:"Slope of horizontal / vertical lines",
 q:"Which statement about slopes is correct?",
 opts:[
  "A line parallel to the x-axis has slope 0; a line parallel to the y-axis has undefined slope.",
  "A line parallel to the x-axis has undefined slope; a line parallel to the y-axis has slope 0.",
  "Both have slope 0.",
  "Both have undefined slope."],
 ans:0,
 why:[
  "Correct. Horizontal: θ = 0°, m = tan0° = 0. Vertical: θ = 90°, tan90° is undefined.",
  "The two are swapped — horizontal is the one with slope 0.",
  "A vertical line does not have slope 0; its slope is undefined.",
  "A horizontal line has a perfectly defined slope, namely 0."],
 sol:"Parallel to x-axis ⇒ θ = 0° ⇒ m = 0. Parallel to y-axis ⇒ θ = 90° ⇒ tan90° <b>undefined</b> (x = constant)."},

{id:6, lec:"L-1", blk:"Intercepts on the axes", topic:"Meaning of x-intercept",
 q:"The x-intercept of a line is",
 opts:[
  "the x-coordinate of the point where the line meets the x-axis (where y = 0)",
  "the y-coordinate of the point where the line meets the y-axis (where x = 0)",
  "the distance between the two axis-crossing points",
  "always equal to the slope of the line"],
 ans:0,
 why:[
  "Correct. On the x-axis y = 0, so the x-intercept is the x-value of that crossing point.",
  "That describes the <b>y</b>-intercept, read where x = 0.",
  "The intercept is a single coordinate, not the length of a segment between the crossings.",
  "The intercept and the slope are unrelated quantities."],
 sol:"At the x-axis, <b>y = 0</b>; the line's x-coordinate there is the x-intercept. At the y-axis, x = 0, giving the y-intercept."},

{id:7, lec:"L-1", blk:"Equations of the axes", topic:"Equation of the x-axis",
 q:"The equation of the x-axis is",
 opts:["y = 0", "x = 0", "y = x", "x + y = 0"],
 ans:0,
 why:[
  "Correct. Every point on the x-axis has y-coordinate 0, so its equation is <b>y = 0</b>.",
  "x = 0 is the <b>y</b>-axis, where every point has x-coordinate 0.",
  "y = x is the 45° line through the origin, not an axis.",
  "x + y = 0 is the line y = −x through the origin, not an axis."],
 sol:"x-axis: <b>y = 0</b>; y-axis: x = 0. A line parallel to the x-axis is y = a; parallel to the y-axis is x = a."},

{id:8, lec:"L-1", blk:"Equations parallel to the axes", topic:"Line parallel to the y-axis",
 q:"The equation of a line parallel to the y-axis passing through (3, −7) is",
 opts:["x = 3", "y = −7", "x = −7", "y = 3"],
 ans:0,
 why:[
  "Correct. A line parallel to the y-axis is vertical: x = constant = the point's x-coordinate = <b>3</b>.",
  "y = −7 is parallel to the x-axis (horizontal), not the y-axis.",
  "The constant must be the x-coordinate 3, not the y-coordinate.",
  "y = 3 is horizontal and does not even pass through the given point."],
 sol:"Parallel to the y-axis ⇒ vertical ⇒ x = constant. It passes through x = 3, so the line is <b>x = 3</b>."},

{id:9, lec:"L-1", blk:"Reading the sign of the slope", topic:"Line bisecting the first quadrant",
 q:"A line through the origin that bisects the first quadrant (inclination 45°) has slope",
 opts:["1", "−1", "0", "undefined"],
 ans:0,
 why:[
  "Correct. m = tan45° = <b>1</b>.",
  "−1 is tan135°, the line bisecting the second quadrant, falling to the right.",
  "Slope 0 is horizontal (θ = 0°), not the 45° bisector.",
  "An undefined slope is vertical (θ = 90°), not 45°."],
 sol:"The first-quadrant bisector has θ = 45°, so m = tan45° = <b>1</b> (the line y = x)."},

{id:10, lec:"L-1", blk:"Reading the sign of the slope", topic:"Sign of a negative slope",
 q:"If a line's slope is negative, the line",
 opts:[
  "falls from left to right (obtuse inclination)",
  "rises from left to right (acute inclination)",
  "is horizontal",
  "is vertical"],
 ans:0,
 why:[
  "Correct. m < 0 ⇒ θ is obtuse (between 90° and 180°) ⇒ the line <b>falls</b> to the right.",
  "A rising line has positive slope and acute inclination.",
  "A horizontal line has slope exactly 0, not negative.",
  "A vertical line has undefined slope, not a negative one."],
 sol:"m &gt; 0 ⇒ rises (acute θ); m < 0 ⇒ <b>falls</b> (obtuse θ); m = 0 ⇒ horizontal; m undefined ⇒ vertical."},

{id:11, lec:"L-1", blk:"Collinearity via slopes", topic:"Collinear points",
 q:"The points (1, 2), (3, 6) and (4, 8) are",
 opts:[
  "collinear, because every pair gives slope 2",
  "the vertices of a triangle",
  "collinear, because every pair gives slope 1",
  "not collinear"],
 ans:0,
 why:[
  "Correct. Slope (1,2)-(3,6) = 4/2 = 2 and (3,6)-(4,8) = 2/1 = 2; equal slopes through a shared point ⇒ collinear.",
  "Three points with a common slope cannot form a triangle; they lie on one line.",
  "The common slope is 2, not 1: (6 − 2)/(3 − 1) = 2.",
  "They are collinear — all three satisfy y = 2x."],
 sol:"Slope (1,2)→(3,6) = (6 − 2)/(3 − 1) = 2; slope (3,6)→(4,8) = (8 − 6)/(4 − 3) = 2. Equal slopes sharing a point ⇒ the three are <b>collinear</b> (all on y = 2x)."},

/* ---------------- L-2 ---------------- */
{id:12, lec:"L-2", blk:"Two-point form", topic:"Line through two points",
 q:"The equation of the line through (2, 3) and (4, 5) is",
 opts:["x − y + 1 = 0", "x − y − 1 = 0", "x + y − 5 = 0", "x − y + 5 = 0"],
 ans:0,
 why:[
  "Correct. m = 1, then y − 3 = 1·(x − 2) ⇒ y = x + 1 ⇒ <b>x − y + 1 = 0</b>.",
  "This is y = x − 1, which passes through (2,1) not (2,3) — the constant sign is wrong.",
  "x + y = 5 has slope −1; this line rises with slope +1.",
  "y = x + 5 passes through (2,7), not (2,3)."],
 sol:"m = (5 − 3)/(4 − 2) = 1; y − 3 = 1·(x − 2) ⇒ y = x + 1 ⇒ <b>x − y + 1 = 0</b>. Check (4,5): 4 − 5 + 1 = 0 ✓."},

{id:13, lec:"L-2", blk:"Double-intercept form", topic:"Line from both intercepts",
 q:"The equation of the line whose x-intercept is 4 and y-intercept is 3 is",
 opts:["3x + 4y = 12", "4x + 3y = 12", "3x + 4y = 7", "4x + 3y = 24"],
 ans:0,
 why:[
  "Correct. x/4 + y/3 = 1, multiply by 12 ⇒ <b>3x + 4y = 12</b>.",
  "The coefficients are swapped: x/4 gives a coefficient 3 for x (from the LCM), not 4.",
  "7 would come from adding the intercepts; the correct constant is the LCM 12.",
  "Multiplying x/4 + y/3 = 1 by 12 gives 3x + 4y, not 4x + 3y = 24."],
 sol:"Double-intercept: x/a + y/b = 1 ⇒ x/4 + y/3 = 1; ×12 ⇒ <b>3x + 4y = 12</b>. Check x-int: y = 0 ⇒ x = 4 ✓."},

{id:14, lec:"L-2", blk:"Point-slope form", topic:"Line from slope and a point",
 q:"The line through (1, −1) with slope 2 is",
 opts:["y = 2x − 3", "y = 2x + 1", "y = 2x − 1", "y = 2x + 3"],
 ans:0,
 why:[
  "Correct. y − (−1) = 2(x − 1) ⇒ y + 1 = 2x − 2 ⇒ <b>y = 2x − 3</b>.",
  "This takes the point as (1, +1) rather than (1, −1).",
  "A sign slip in the expansion: −2 − 1 = −3, not −1.",
  "This adds the constants instead of subtracting; it passes through (1, 5)."],
 sol:"y − y₁ = m(x − x₁) ⇒ y + 1 = 2(x − 1) = 2x − 2 ⇒ <b>y = 2x − 3</b>. Check (1,−1): 2 − 3 = −1 ✓."},

{id:15, lec:"L-2", blk:"Slope-intercept form", topic:"Line from slope and y-intercept",
 q:"A line has slope 3 and y-intercept −2. Its equation is",
 opts:["y = 3x − 2", "y = −2x + 3", "y = 3x + 2", "3x + 2y = 0"],
 ans:0,
 why:[
  "Correct. y = mx + c = <b>3x − 2</b> directly.",
  "This confuses slope with intercept — slope is 3, intercept is −2, not the reverse.",
  "The intercept is −2, so the constant is −2, not +2.",
  "This is a line through the origin; a y-intercept of −2 means the constant term is not zero."],
 sol:"Slope-intercept form y = mx + c with m = 3, c = −2 gives <b>y = 3x − 2</b>."},

{id:16, lec:"L-2", blk:"Equal intercepts", topic:"Equal intercepts through a point",
 q:"A line cuts off equal intercepts on the axes and passes through (3, 5). Its equation is",
 opts:["x + y = 8", "x − y = 8", "x + y = 2", "5x + 3y = 8"],
 ans:0,
 why:[
  "Correct. Equal intercepts a = b ⇒ x + y = a (slope −1); through (3,5): 3 + 5 = <b>8</b>.",
  "x − y = 8 has slope +1 and equal-and-<i>opposite</i> intercepts, not equal ones.",
  "x + y = 2 does not pass through (3,5): 3 + 5 = 8, not 2.",
  "This is not of the equal-intercept form x + y = a at all."],
 sol:"Equal intercepts a = b ⇒ x/a + y/a = 1 ⇒ x + y = a (slope −1). Through (3,5): a = 3 + 5 = 8 ⇒ <b>x + y = 8</b>."},

{id:17, lec:"L-2", blk:"Equal-and-opposite intercepts", topic:"Intercepts equal in magnitude, opposite in sign",
 q:"A line makes intercepts equal in magnitude but opposite in sign and passes through (2, −1). Its equation is",
 opts:["x − y = 3", "x + y = 3", "x − y = 1", "x − y = −3"],
 ans:0,
 why:[
  "Correct. Such a line is x − y = a (slope +1); through (2,−1): 2 − (−1) = <b>3</b>.",
  "x + y = 3 has slope −1 (equal intercepts), not equal-and-opposite.",
  "The constant from (2,−1) is 2 + 1 = 3, not 1.",
  "2 − (−1) = +3, so the sign of the constant is positive."],
 sol:"Equal magnitude, opposite sign ⇒ a = −b ⇒ x/a − y/a = 1 ⇒ x − y = a (slope +1). Through (2,−1): a = 2 − (−1) = 3 ⇒ <b>x − y = 3</b>."},

{id:18, lec:"L-2", blk:"Two-point form", topic:"Line through two points (slope −1)",
 q:"The equation of the line through (2, −1) and (−3, 4) is",
 opts:["x + y = 1", "x + y = −1", "x − y = 3", "x + y = 3"],
 ans:0,
 why:[
  "Correct. m = (4 − (−1))/(−3 − 2) = 5/(−5) = −1; y + 1 = −1(x − 2) ⇒ <b>x + y = 1</b>.",
  "Check (2,−1): 2 + (−1) = 1, not −1, so the constant must be +1.",
  "The slope here is −1, giving x + y (not x − y) on the left.",
  "x + y = 3 fails at (2,−1): 2 − 1 = 1, not 3."],
 sol:"m = (4 + 1)/(−3 − 2) = 5/(−5) = −1; y − (−1) = −1(x − 2) ⇒ y + 1 = −x + 2 ⇒ <b>x + y = 1</b>."},

{id:19, lec:"L-2", blk:"Choosing a form", topic:"Which form fits the data",
 q:"You are given the slope of a line and its y-intercept. The quickest form to write it in is the",
 opts:[
  "slope-intercept form y = mx + c",
  "two-point form",
  "normal form x cosα + y sinα = p",
  "double-intercept form x/a + y/b = 1"],
 ans:0,
 why:[
  "Correct. Slope m and y-intercept c plug straight into y = mx + c with no extra work.",
  "The two-point form needs two points, neither of which is given.",
  "The normal form needs the perpendicular length p and angle α, not slope and intercept.",
  "The double-intercept form needs <i>both</i> intercepts; only the y-intercept is given."],
 sol:"Slope + y-intercept is exactly the data for <b>y = mx + c</b>. Two points → two-point; slope + a point → point-slope; both intercepts → double-intercept."},

/* ---------------- L-3 ---------------- */
{id:20, lec:"L-3", blk:"Normal form", topic:"Line from perpendicular length and angle",
 q:"The length of the perpendicular from the origin to a line is 4, and the line makes an angle of 120° with the positive x-axis. Its equation is",
 opts:["√3 x + y = 8", "x + √3 y = 8", "√3 x − y = 8", "√3 x + y = 4"],
 ans:0,
 why:[
  "Correct. The perpendicular's angle α = 120° − 90° = 30°; x cos30° + y sin30° = 4 ⇒ (√3/2)x + (1/2)y = 4 ⇒ <b>√3 x + y = 8</b>.",
  "This uses α = 60° instead of 30°, swapping the cos and sin coefficients.",
  "A sign slip: both cos30° and sin30° are positive here, so both terms are +.",
  "After doubling (√3/2)x + (1/2)y = 4 the constant becomes 8, not 4."],
 sol:"Line inclination 120° ⇒ its perpendicular makes α = 120° − 90° = 30° with +x-axis, p = 4. x cosα + y sinα = p ⇒ x·(√3/2) + y·(1/2) = 4 ⇒ <b>√3 x + y = 8</b>."},

{id:21, lec:"L-3", blk:"Normal form", topic:"Normal form assembly",
 q:"The equation of the line with perpendicular distance 5 from the origin, the perpendicular making 30° with the positive x-axis, is",
 opts:["√3 x + y = 10", "x + √3 y = 10", "√3 x + y = 5", "x + √3 y = 5"],
 ans:0,
 why:[
  "Correct. x cos30° + y sin30° = 5 ⇒ (√3/2)x + (1/2)y = 5 ⇒ <b>√3 x + y = 10</b>.",
  "This swaps the cos and sin, using α = 60° by mistake.",
  "Clearing the halves doubles the constant: 5 becomes 10.",
  "Both the coefficients are swapped and the constant is left undoubled."],
 sol:"x cosα + y sinα = p with α = 30°, p = 5: (√3/2)x + (1/2)y = 5; ×2 ⇒ <b>√3 x + y = 10</b>."},

{id:22, lec:"L-3", blk:"Parametric form", topic:"Points a fixed distance from a given point",
 q:"A line through A(3, 2) has slope 3/4. The points on it that are 5 units from A are",
 opts:["(7, 5) and (−1, −1)", "(7, 5) and (−1, 1)", "(6, 5) and (0, −1)", "(7, −1) and (−1, 5)"],
 ans:0,
 why:[
  "Correct. cosθ = 4/5, sinθ = 3/5; x = 3 ± 5(4/5) = 7 or −1, y = 2 ± 5(3/5) = 5 or −1 ⇒ <b>(7,5) and (−1,−1)</b>.",
  "The second point's y should be 2 − 3 = −1, not +1; both coordinates change sign together.",
  "The step is ±4 in x and ±3 in y, giving 3±4 = 7 or −1, not 6 or 0.",
  "The + case pairs the +x with +y: (7,5), and the − case pairs −x with −y: (−1,−1); they do not cross."],
 sol:"tanθ = 3/4 ⇒ cosθ = 4/5, sinθ = 3/5. x = x₁ + r cosθ = 3 ± 5·(4/5) = 7 or −1; y = y₁ + r sinθ = 2 ± 5·(3/5) = 5 or −1 ⇒ <b>(7,5) and (−1,−1)</b>."},

{id:23, lec:"L-3", blk:"Reducing Ax+By+C=0", topic:"Slope from general form",
 q:"The slope of the line 3x − 4y + 12 = 0 is",
 opts:["3/4", "−3/4", "4/3", "−4/3"],
 ans:0,
 why:[
  "Correct. slope = −A/B = −3/(−4) = <b>3/4</b>.",
  "This forgets that B = −4 is already negative: −A/B = −3/(−4) = +3/4.",
  "This inverts the ratio — slope is −A/B = −3/−4, not −B/A.",
  "Both the inversion and a sign error are present here."],
 sol:"For Ax + By + C = 0, slope = −A/B. Here A = 3, B = −4 ⇒ slope = −3/(−4) = <b>3/4</b>."},

{id:24, lec:"L-3", blk:"Reducing Ax+By+C=0", topic:"x-intercept from general form",
 q:"The x-intercept of the line 2x + 3y − 6 = 0 is",
 opts:["3", "2", "−3", "6"],
 ans:0,
 why:[
  "Correct. x-intercept = −C/A = −(−6)/2 = <b>3</b>; equivalently set y = 0 ⇒ 2x = 6 ⇒ x = 3.",
  "2 is the <b>y</b>-intercept (−C/B = 6/3 = 2), not the x-intercept.",
  "The sign is wrong: −C/A = −(−6)/2 = +3.",
  "6 is the constant moved across, not yet divided by the coefficient of x."],
 sol:"Set y = 0: 2x − 6 = 0 ⇒ x = 3. (Formula: x-int = −C/A = −(−6)/2 = <b>3</b>.)"},

{id:25, lec:"L-3", blk:"Reducing Ax+By+C=0", topic:"Distance of origin from a line",
 q:"The perpendicular distance of the origin from the line 3x + 4y − 10 = 0 is",
 opts:["2", "10", "5", "2/5"],
 ans:0,
 why:[
  "Correct. d = |C|/√(A²+B²) = 10/√(9+16) = 10/5 = <b>2</b>.",
  "10 is just |C|; it must be divided by √(A²+B²) = 5.",
  "5 is √(A²+B²), the denominator, not the full distance.",
  "This inverts the fraction — the distance is 10/5, not 5/10."],
 sol:"d = |C|/√(A²+B²) = |−10|/√(3²+4²) = 10/5 = <b>2</b>."},

{id:26, lec:"L-3", blk:"Point of intersection", topic:"Intersection of two lines",
 q:"The point of intersection of x + y = 5 and x − y = 1 is",
 opts:["(3, 2)", "(2, 3)", "(3, −2)", "(4, 1)"],
 ans:0,
 why:[
  "Correct. Adding: 2x = 6 ⇒ x = 3; then y = 5 − 3 = 2 ⇒ <b>(3, 2)</b>.",
  "This swaps x and y; x − y = 1 needs x the larger, so x = 3, y = 2.",
  "y = 2 from the equations, not −2: x − y = 1 with x = 3 gives y = 2.",
  "(4,1): 4 + 1 = 5 ✓ but 4 − 1 = 3 ≠ 1, so it fails the second equation."],
 sol:"Add the two: (x + y) + (x − y) = 5 + 1 ⇒ 2x = 6 ⇒ x = 3; then y = 5 − 3 = 2 ⇒ <b>(3, 2)</b>."},

{id:27, lec:"L-3", blk:"Concurrency", topic:"Concurrency condition",
 q:"Three lines a₁x + b₁y + c₁ = 0, a₂x + b₂y + c₂ = 0, a₃x + b₃y + c₃ = 0 are concurrent if and only if",
 opts:[
  "det[[a₁,b₁,c₁],[a₂,b₂,c₂],[a₃,b₃,c₃]] = 0",
  "a₁a₂a₃ + b₁b₂b₃ + c₁c₂c₃ = 0",
  "a₁/a₂ = b₁/b₂ = c₁/c₂",
  "a₁a₂ + b₁b₂ + c₁c₂ = 0"],
 ans:0,
 why:[
  "Correct. A common point exists iff the 3×3 coefficient determinant <b>vanishes</b>.",
  "This is not a determinant and has no geometric meaning for concurrency.",
  "That proportionality says the three lines are <i>parallel/coincident</i>, not concurrent.",
  "That is a dot-product-like condition unrelated to three lines meeting at a point."],
 sol:"Three lines meet at one point iff the system has a solution, i.e. the coefficient determinant <b>det[[a₁,b₁,c₁],[a₂,b₂,c₂],[a₃,b₃,c₃]] = 0</b>."},

{id:28, lec:"L-3", blk:"Concurrency", topic:"Finding the constant for concurrency",
 q:"For what value of k are the lines x + y − 3 = 0, x − y − 1 = 0 and 2x + y + k = 0 concurrent?",
 opts:["−5", "5", "−3", "3"],
 ans:0,
 why:[
  "Correct. The first two meet at (2, 1); substituting into the third: 4 + 1 + k = 0 ⇒ k = <b>−5</b>.",
  "This is the negative of the answer — 2(2) + 1 + k = 0 gives k = −5, not +5.",
  "−3 comes from dropping the y-term at (2,1): the full value is 4 + 1 = 5.",
  "The constant must cancel +5, so k = −5, not +3."],
 sol:"x + y = 3 and x − y = 1 give x = 2, y = 1. The third must pass through (2,1): 2(2) + 1 + k = 0 ⇒ 5 + k = 0 ⇒ k = <b>−5</b>."},

{id:29, lec:"L-3", blk:"Normal form", topic:"Sign convention in normal form",
 q:"When reducing a line to normal form x cosα + y sinα = p, the convention is to",
 opts:[
  "keep p ≥ 0 by choosing the sign of √(A²+B²) so the constant is positive",
  "always divide by +√(A²+B²) regardless of sign",
  "keep p ≤ 0",
  "set α equal to the line's own inclination"],
 ans:0,
 why:[
  "Correct. p is a length, so it must be <b>non-negative</b>; pick the sign of the root to make the constant positive.",
  "If the constant comes out negative you must divide by −√(A²+B²) instead, to keep p ≥ 0.",
  "p is a distance and can never be negative.",
  "α is the angle of the <i>perpendicular</i> from the origin, which differs from the line's inclination by 90°."],
 sol:"Normal form needs <b>p ≥ 0</b> (p = ⊥ distance from O). Divide Ax + By + C = 0 by ±√(A²+B²), choosing the sign that makes the right-hand constant positive."},

{id:30, lec:"L-3", blk:"Parametric form", topic:"Sign of the parameter r",
 q:"In the parametric form (x − x₁)/cosθ = (y − y₁)/sinθ = r for a line through Q(x₁, y₁), the quantity r represents",
 opts:[
  "the signed distance of the point (x, y) from Q along the line",
  "the slope of the line",
  "the perpendicular distance of (x, y) from Q",
  "the inclination θ of the line"],
 ans:0,
 why:[
  "Correct. r is the <b>signed distance</b> from Q measured along the line; r &gt; 0 one way, r < 0 the other.",
  "The slope is tanθ, a separate quantity from the parameter r.",
  "r is the distance <i>along</i> the line, not perpendicular to it.",
  "θ is the inclination used inside cosθ, sinθ; r is the distance, not the angle."],
 sol:"x = x₁ + r cosθ, y = y₁ + r sinθ, so r is the <b>signed distance from Q</b> along the line. Both points a distance d from Q come from r = ±d."},

/* ---------------- L-4 ---------------- */
{id:31, lec:"L-4", blk:"Angle between two lines", topic:"Tangent of the angle",
 q:"The tangent of the acute angle between x − y + 5 = 0 and x + 2y = 0 is",
 opts:["3", "1/3", "−3", "1"],
 ans:0,
 why:[
  "Correct. m₁ = 1, m₂ = −1/2; tanθ = |(1 − (−1/2))/(1 + 1(−1/2))| = |(3/2)/(1/2)| = <b>3</b>.",
  "1/3 inverts the ratio — the numerator 3/2 exceeds the denominator 1/2.",
  "The acute-angle tangent is taken as a positive modulus, so +3, not −3.",
  "tanθ = 1 would mean a 45° angle; here the ratio evaluates to 3."],
 sol:"Slopes m₁ = 1, m₂ = −1/2. tanθ = |(m₁ − m₂)/(1 + m₁m₂)| = |(1 + 1/2)/(1 − 1/2)| = |(3/2)/(1/2)| = <b>3</b>."},

{id:32, lec:"L-4", blk:"Angle between two lines", topic:"Angle from two slopes",
 q:"The tangent of the acute angle between two lines of slopes 2 and 3 is",
 opts:["1/7", "7", "5", "1/5"],
 ans:0,
 why:[
  "Correct. tanθ = |(2 − 3)/(1 + 2·3)| = |−1/7| = <b>1/7</b>.",
  "7 inverts the fraction; the denominator 1 + 6 = 7 sits below.",
  "5 = 2 + 3 just adds the slopes, which is not the formula.",
  "The numerator is |2 − 3| = 1, not |2 + 3| = 5, so this is wrong."],
 sol:"tanθ = |(m₁ − m₂)/(1 + m₁m₂)| = |(2 − 3)/(1 + 6)| = |−1/7| = <b>1/7</b>."},

{id:33, lec:"L-4", blk:"Parallel lines", topic:"Parallel line through a point",
 q:"The line parallel to 3x + 2y + 4 = 0 and passing through (1, 1) is",
 opts:["3x + 2y = 5", "3x + 2y = 4", "2x − 3y = 5", "3x + 2y = 0"],
 ans:0,
 why:[
  "Correct. Parallel ⇒ 3x + 2y + c = 0; through (1,1): 3 + 2 + c = 0 ⇒ c = −5 ⇒ <b>3x + 2y = 5</b>.",
  "This keeps the original constant 4; but (1,1) forces 3 + 2 = 5 on the right.",
  "2x − 3y is <i>perpendicular</i> to 3x + 2y, not parallel.",
  "3x + 2y = 0 passes through the origin, not (1,1)."],
 sol:"Parallel lines share the x,y coefficients: 3x + 2y + c = 0. Through (1,1): 3(1) + 2(1) + c = 0 ⇒ c = −5 ⇒ <b>3x + 2y = 5</b>."},

{id:34, lec:"L-4", blk:"Perpendicular lines", topic:"Perpendicular line through a point",
 q:"The line perpendicular to 2x − y = 7 and passing through (0, 2) is",
 opts:["x + 2y = 4", "2x − y = 2", "x − 2y = 4", "x + 2y = 2"],
 ans:0,
 why:[
  "Correct. ⊥ to 2x − y is x + 2y = c (swap and flip a sign); through (0,2): 0 + 4 = c ⇒ <b>x + 2y = 4</b>.",
  "This is parallel to the given line, not perpendicular.",
  "x − 2y uses the wrong sign; the perpendicular to 2x − y is x + 2y.",
  "Through (0,2): 0 + 2(2) = 4, so the constant is 4, not 2."],
 sol:"⊥ to 2x − y + c = 0 is obtained by swapping coefficients and flipping one sign: x + 2y = c. Through (0,2): 0 + 2(2) = c ⇒ c = 4 ⇒ <b>x + 2y = 4</b>."},

{id:35, lec:"L-4", blk:"Perpendicular condition", topic:"Testing perpendicularity",
 q:"Which pair of lines is perpendicular?",
 opts:[
  "2x + 3y = 1 and 3x − 2y = 5",
  "2x + 3y = 1 and 2x + 3y = 5",
  "2x + 3y = 1 and 4x + 6y = 5",
  "2x + 3y = 1 and 3x + 2y = 5"],
 ans:0,
 why:[
  "Correct. a₁a₂ + b₁b₂ = 2·3 + 3·(−2) = 6 − 6 = <b>0</b> ⇒ perpendicular.",
  "These are <i>parallel</i> (same coefficients), not perpendicular.",
  "4x + 6y is a multiple of 2x + 3y — parallel again.",
  "a₁a₂ + b₁b₂ = 2·3 + 3·2 = 12 ≠ 0, so not perpendicular."],
 sol:"Perpendicular ⇔ a₁a₂ + b₁b₂ = 0. For 2x + 3y and 3x − 2y: (2)(3) + (3)(−2) = 6 − 6 = <b>0</b> ✓."},

{id:36, lec:"L-4", blk:"Perpendicular distance", topic:"Distance of a point from a line",
 q:"The perpendicular distance of the point (1, 1) from the line 3x + 4y − 5 = 0 is",
 opts:["2/5", "2", "5/2", "12/5"],
 ans:0,
 why:[
  "Correct. d = |3 + 4 − 5|/√(9+16) = |2|/5 = <b>2/5</b>.",
  "2 is the numerator |ax₁+by₁+c| before dividing by √(A²+B²) = 5.",
  "This inverts the fraction — it is 2/5, not 5/2.",
  "12/5 would use a numerator of 12; here 3 + 4 − 5 = 2."],
 sol:"d = |a x₁ + b y₁ + c|/√(a²+b²) = |3(1) + 4(1) − 5|/√(3²+4²) = |2|/5 = <b>2/5</b>."},

{id:37, lec:"L-4", blk:"Distance between parallels", topic:"Gap between two parallel lines",
 q:"The distance between the parallel lines 3x + 4y + 7 = 0 and 3x + 4y − 3 = 0 is",
 opts:["2", "10", "4/5", "1"],
 ans:0,
 why:[
  "Correct. d = |c₁ − c₂|/√(A²+B²) = |7 − (−3)|/5 = 10/5 = <b>2</b>.",
  "10 is |c₁ − c₂|; it must be divided by √(9+16) = 5.",
  "4/5 would come from |7 − 3| = 4, but the constants are +7 and −3, giving 10.",
  "1 would be the gap only if |c₁ − c₂| = 5; here it is 10."],
 sol:"d = |c₁ − c₂|/√(a²+b²) = |7 − (−3)|/√(3²+4²) = 10/5 = <b>2</b>."},

{id:38, lec:"L-4", blk:"Side of a point", topic:"Same or opposite side",
 q:"The points (3, 4) and (2, −6) with respect to the line 3x − 4y − 8 = 0 lie on",
 opts:[
  "opposite sides, because the values have opposite signs",
  "the same side, because both values are negative",
  "the line itself",
  "the same side, because both values are positive"],
 ans:0,
 why:[
  "Correct. L(3,4) = 9 − 16 − 8 = −15 and L(2,−6) = 6 + 24 − 8 = 22; opposite signs ⇒ <b>opposite sides</b>.",
  "L(2,−6) = 22 is positive, so the two values are not both negative.",
  "Neither value is 0, so neither point lies on the line.",
  "L(3,4) = −15 is negative, so they are not both positive."],
 sol:"L = 3x − 4y − 8. L(3,4) = 9 − 16 − 8 = −15 (−); L(2,−6) = 6 + 24 − 8 = 22 (+). Opposite signs ⇒ <b>opposite sides</b>."},

{id:39, lec:"L-4", blk:"Perpendicular distance", topic:"Point on an axis at a given distance",
 q:"The points on the y-axis whose perpendicular distance from 4x − 3y − 12 = 0 is 3 are",
 opts:["(0, 1) and (0, −9)", "(0, 1) and (0, 9)", "(0, −1) and (0, 9)", "(0, 3) and (0, −3)"],
 ans:0,
 why:[
  "Correct. P(0,k): |−3k − 12|/5 = 3 ⇒ |3k + 12| = 15 ⇒ k = 1 or −9 ⇒ <b>(0,1) and (0,−9)</b>.",
  "The second root is k = −9, not +9: 3k + 12 = −15 ⇒ k = −9.",
  "The first root is k = +1, not −1: 3k + 12 = 15 ⇒ k = 1.",
  "(0,±3) do not satisfy |3k + 12| = 15."],
 sol:"P(0,k): |4(0) − 3k − 12|/√(4²+3²) = 3 ⇒ |3k + 12| = 15 ⇒ 3k + 12 = ±15 ⇒ k = 1 or k = −9 ⇒ <b>(0,1) and (0,−9)</b>."},

{id:40, lec:"L-4", blk:"Image in a line", topic:"Reflection of a point",
 q:"The image of the point (4, −13) in the line mirror 5x + y + 6 = 0 is",
 opts:["(−1, −14)", "(−1, −12)", "(1, −14)", "(−6, −15)"],
 ans:0,
 why:[
  "Correct. The factor is −2(5·4 − 13 + 6)/(25+1) = −2(13)/26 = −1; x = 4 − 5 = −1, y = −13 − 1 = <b>−14</b>.",
  "y = −13 + (1)(−1) = −14, not −12 — a sign slip on the y-step.",
  "x = 4 + 5(−1) = −1, not +1; the x-step is −5.",
  "These are the steps added twice over; the correct image is (−1, −14)."],
 sol:"(x − 4)/5 = (y + 13)/1 = −2(5·4 − 13 + 6)/(5²+1²) = −2(13)/26 = −1. So x = 4 + 5(−1) = −1, y = −13 + 1(−1) = <b>−14</b> ⇒ (−1, −14)."},

{id:41, lec:"L-4", blk:"Foot of perpendicular", topic:"Foot of the perpendicular",
 q:"The foot of the perpendicular from (1, 2) to the line x + y − 5 = 0 is",
 opts:["(2, 3)", "(3, 2)", "(2.5, 2.5)", "(0, 5)"],
 ans:0,
 why:[
  "Correct. factor = −(1 + 2 − 5)/(1+1) = 1; x = 1 + 1 = 2, y = 2 + 1 = 3 ⇒ <b>(2, 3)</b>.",
  "(3,2) is on the line but is not the foot from (1,2); the perpendicular lands at (2,3).",
  "(2.5,2.5) is the point of x + y = 5 nearest the origin, not the foot from (1,2).",
  "(0,5) lies on the line but the perpendicular from (1,2) does not reach it."],
 sol:"(x − 1)/1 = (y − 2)/1 = −(1 + 2 − 5)/(1²+1²) = −(−2)/2 = 1. So x = 1 + 1 = 2, y = 2 + 1 = 3 ⇒ <b>(2, 3)</b>. Check on line: 2 + 3 = 5 ✓."},

{id:42, lec:"L-4", blk:"Reflection in special lines", topic:"Image in the x-axis",
 q:"The reflection of the point (5, −3) in the x-axis is",
 opts:["(5, 3)", "(−5, −3)", "(−3, 5)", "(−5, 3)"],
 ans:0,
 why:[
  "Correct. Reflecting in the x-axis flips the sign of y: (α, β) → (α, −β) = <b>(5, 3)</b>.",
  "(−5,−3) is the reflection in the <b>y</b>-axis (x flips), not the x-axis.",
  "(−3,5) is the reflection in the line y = x (coordinates swap).",
  "(−5,3) is the reflection through the origin, flipping both signs."],
 sol:"Reflection in the x-axis sends (α, β) → (α, −β). So (5, −3) → <b>(5, 3)</b>."},

{id:43, lec:"L-4", blk:"Line at a given angle", topic:"Lines through a point at 45° to a line",
 q:"A line through (1, 2) makes 45° with 2x + 3y = 10. One such line has slope",
 opts:["1/5", "−2/3", "2/3", "3/2"],
 ans:0,
 why:[
  "Correct. m₁ = −2/3; tan45° = 1 = |(m + 2/3)/(1 − 2m/3)| ⇒ m = 1/5 (or m = −5) ⇒ slope <b>1/5</b>.",
  "−2/3 is the slope of the <i>given</i> line, which makes 0°, not 45°, with itself.",
  "+2/3 is neither the given slope nor a 45° solution.",
  "3/2 is the slope perpendicular to the given line (90°, not 45°)."],
 sol:"Slope of 2x + 3y = 10 is −2/3. tan45° = 1 = |(m + 2/3)/(1 − 2m/3)| = |(3m + 2)/(3 − 2m)| ⇒ 3m + 2 = ±(3 − 2m) ⇒ m = <b>1/5</b> or m = −5."},

{id:44, lec:"L-4", blk:"Perpendicular construction", topic:"Perpendicular to ax+by+c=0",
 q:"The general line perpendicular to ax + by + c = 0 is",
 opts:["bx − ay + λ = 0", "ax + by + λ = 0", "−ax + by + λ = 0", "bx + ay + λ = 0"],
 ans:0,
 why:[
  "Correct. Swap a and b <b>and flip one sign</b>: bx − ay + λ = 0, so that a·b + b·(−a) = 0.",
  "ax + by + λ keeps the same coefficients — that is the <i>parallel</i> family.",
  "−ax + by + λ is the common wrong answer; its dot product −a² + b² is not generally 0.",
  "bx + ay + λ swaps the coefficients but forgets to flip a sign, so it is not perpendicular."],
 sol:"Perpendicular ⇔ coefficient dot product 0. Take bx − ay + λ = 0: (a)(b) + (b)(−a) = 0 ✓. (Parallel keeps ax + by + λ = 0.)"},

{id:45, lec:"L-4", blk:"Isosceles right triangle", topic:"Equal sides making 45° with the hypotenuse",
 q:"The hypotenuse of an isosceles right triangle is 3x + 4y = 4 and the right-angle vertex is (2, 2). The equal sides make 45° with the hypotenuse, giving slopes",
 opts:["1/7 and −7", "−3/4 and 4/3", "1/7 and 7", "3/4 and −4/3"],
 ans:0,
 why:[
  "Correct. m₁ = −3/4; 1 = |(m + 3/4)/(1 − 3m/4)| ⇒ 4m + 3 = ±(4 − 3m) ⇒ m = <b>1/7 or −7</b>.",
  "−3/4 is the hypotenuse's slope (0° to itself), and 4/3 is its perpendicular (90°), neither is 45°.",
  "The second slope is −7, not +7; the ± gives one positive and one negative.",
  "These are the hypotenuse slope and its perpendicular, not the 45° sides."],
 sol:"Slope of 3x + 4y − 4 = 0 is −3/4. tan45° = 1 = |(m + 3/4)/(1 − 3m/4)| = |(4m + 3)/(4 − 3m)| ⇒ 4m + 3 = ±(4 − 3m) ⇒ m = <b>1/7 or −7</b>."},

{id:46, lec:"L-4", blk:"Distance of origin", topic:"Origin distance, quick read",
 q:"The perpendicular distance of the origin from 5x + 12y − 26 = 0 is",
 opts:["2", "26", "13", "26/17"],
 ans:0,
 why:[
  "Correct. d = |−26|/√(25+144) = 26/13 = <b>2</b>.",
  "26 is just |C|; divide by √(A²+B²) = 13.",
  "13 is the denominator √(25+144), not the distance itself.",
  "√(A²+B²) = 13, not 17; 26/13 = 2."],
 sol:"d = |C|/√(A²+B²) = 26/√(5²+12²) = 26/13 = <b>2</b>."},

/* ---------------- L-5 ---------------- */
{id:47, lec:"L-5", blk:"Family of lines", topic:"What L₁ + λL₂ = 0 represents",
 q:"For lines L₁ = 0 and L₂ = 0, the family L₁ + λL₂ = 0 (λ ∈ ℝ) represents",
 opts:[
  "every line through the point of intersection of L₁ and L₂",
  "every line parallel to L₁",
  "the single angle bisector of L₁ and L₂",
  "all lines at a fixed distance from L₁"],
 ans:0,
 why:[
  "Correct. The equation is satisfied at L₁ ∩ L₂ for every λ, so it is the <b>pencil of lines through that fixed point</b>.",
  "Members of the family have varying slopes, so they are not all parallel to L₁.",
  "The bisector is a specific member; the family is the whole pencil, not one line.",
  "Distance from L₁ is not preserved across the family."],
 sol:"At the intersection both L₁ = 0 and L₂ = 0, so L₁ + λL₂ = 0 holds there for <b>every</b> λ. Hence the family is all lines through the fixed point L₁ ∩ L₂."},

{id:48, lec:"L-5", blk:"Family of lines", topic:"Member through a given point",
 q:"The line through the intersection of 3x − 4y + 6 = 0 and x + y + 2 = 0 that also passes through (1, 2) is",
 opts:["2x − 3y + 4 = 0", "2x − y + 4 = 0", "x − y + 2 = 0", "3x − 4y + 6 = 0"],
 ans:0,
 why:[
  "Correct. Family (3+λ)x + (λ−4)y + (6+2λ) = 0; at (1,2): 5λ + 1 = 0 ⇒ λ = −1/5 ⇒ <b>2x − 3y + 4 = 0</b>.",
  "2x − y + 4 = 0 is the member parallel to y = 2x + 3, not the one through (1,2).",
  "x − y + 2 = 0 is the equal-and-opposite-intercept member, a different condition.",
  "3x − 4y + 6 = 0 is L₁ itself; it does not pass through (1,2): 3 − 8 + 6 = 1 ≠ 0."],
 sol:"Family: 3x − 4y + 6 + λ(x + y + 2) = 0 ⇒ (3+λ)x + (λ−4)y + (6+2λ) = 0. At (1,2): (3+λ) + 2(λ−4) + (6+2λ) = 5λ + 1 = 0 ⇒ λ = −1/5. Substitute: 14x − 21y + 28 = 0 ⇒ <b>2x − 3y + 4 = 0</b>."},

{id:49, lec:"L-5", blk:"Family of lines", topic:"Member parallel to an axis",
 q:"Among the lines through the intersection of 3x − 4y + 6 = 0 and x + y + 2 = 0, the one parallel to the x-axis is",
 opts:["y = 0", "x = 0", "y = 2", "x = −2"],
 ans:0,
 why:[
  "Correct. Parallel to x-axis ⇒ coeff of x = 0 ⇒ 3 + λ = 0 ⇒ λ = −3; the family becomes −7y = 0 ⇒ <b>y = 0</b>.",
  "x = 0 is parallel to the <i>y</i>-axis, the wrong direction.",
  "Setting coeff of x to zero kills the constant too here, leaving y = 0, not y = 2.",
  "x = −2 is vertical, not parallel to the x-axis."],
 sol:"Family (3+λ)x + (λ−4)y + (6+2λ) = 0. Parallel to x-axis ⇒ coeff of x = 0 ⇒ 3 + λ = 0 ⇒ λ = −3 ⇒ 0·x − 7y + 0 = 0 ⇒ <b>y = 0</b>."},

{id:50, lec:"L-5", blk:"Family of lines", topic:"Member parallel to a given line",
 q:"The line through the intersection of 3x − 4y + 6 = 0 and x + y + 2 = 0 that is parallel to y = 2x + 3 is",
 opts:["2x − y + 4 = 0", "2x − 3y + 4 = 0", "x − y + 2 = 0", "y = 0"],
 ans:0,
 why:[
  "Correct. slope −(3+λ)/(λ−4) = 2 ⇒ λ = 5/3 ⇒ 14x − 7y + 28 = 0 ⇒ <b>2x − y + 4 = 0</b> (slope 2).",
  "2x − 3y + 4 = 0 has slope 2/3, not 2; it is the member through (1,2).",
  "x − y + 2 = 0 has slope 1, not 2.",
  "y = 0 has slope 0, the x-axis-parallel member."],
 sol:"Family (3+λ)x + (λ−4)y + (6+2λ) = 0. Slope = −(3+λ)/(λ−4) = 2 ⇒ −(3+λ) = 2(λ−4) ⇒ 5 = 3λ ⇒ λ = 5/3 ⇒ 14x − 7y + 28 = 0 ⇒ <b>2x − y + 4 = 0</b>."},

{id:51, lec:"L-5", blk:"Area of a parallelogram", topic:"Area from four line equations",
 q:"The area of the parallelogram bounded by x + y − 1 = 0, x + y − 3 = 0, 2x − y − 1 = 0 and 2x − y − 4 = 0 is",
 opts:["2", "6", "3", "1"],
 ans:0,
 why:[
  "Correct. Area = |(c₁−d₁)(c₂−d₂)|/|a₁b₂−a₂b₁| = |(−1+3)(−1+4)|/|1(−1)−2(1)| = |2·3|/3 = 6/3 = <b>2</b>.",
  "6 is the numerator |(c₁−d₁)(c₂−d₂)|; it must be divided by |a₁b₂ − a₂b₁| = 3.",
  "3 is the denominator |a₁b₂ − a₂b₁|, not the area.",
  "1 would need the numerator to equal 3; here it is 6."],
 sol:"With a₁=1,b₁=1,c₁=−1,d₁=−3 and a₂=2,b₂=−1,c₂=−1,d₂=−4: Area = |(c₁−d₁)(c₂−d₂)|/|a₁b₂−a₂b₁| = |(2)(3)|/|(1)(−1)−(2)(1)| = 6/|−3| = <b>2</b>."},

{id:52, lec:"L-5", blk:"Family of lines", topic:"Fixed point of a parametric family",
 q:"Every line of the family (2 + λ)x + (1 − λ)y + (λ − 3) = 0 passes through the fixed point",
 opts:["(1, 2)", "(2, 1)", "(−1, 2)", "(3, −3)"],
 ans:0,
 why:[
  "Correct. Group as (2x + y − 3) + λ(x − y + 1) = 0; solving 2x + y = 3 and x − y = −1 gives <b>(1, 2)</b>.",
  "(2,1): 2x + y − 3 = 2 ≠ 0, so it is not on the base line 2x + y − 3 = 0.",
  "(−1,2): x − y + 1 = −2 ≠ 0, so it fails L₂.",
  "(3,−3): 2x + y − 3 = 0 ✓ but x − y + 1 = 7 ≠ 0, so it fails L₂."],
 sol:"Write the family as (2x + y − 3) + λ(x − y + 1) = 0. The fixed point satisfies both 2x + y − 3 = 0 and x − y + 1 = 0: adding, 3x − 2 = ... solve ⇒ x = 1, y = 2 ⇒ <b>(1, 2)</b>."},

/* ---------------- L-6 ---------------- */
{id:53, lec:"L-6", blk:"Both bisectors", topic:"Equations of the two bisectors",
 q:"The bisectors of the angles between 3x − 4y + 7 = 0 and 12x + 5y − 2 = 0 are",
 opts:[
  "21x + 77y − 101 = 0 and 99x − 27y + 81 = 0",
  "21x + 77y − 101 = 0 and 99x + 27y + 81 = 0",
  "9x − 7y + 5 = 0 and 7x + 9y − 5 = 0",
  "15x + y + 5 = 0 and x − 15y + 9 = 0"],
 ans:0,
 why:[
  "Correct. (3x−4y+7)/5 = ±(12x+5y−2)/13 gives 21x + 77y − 101 = 0 (+) and <b>99x − 27y + 81 = 0</b> (−).",
  "The second bisector is 99x − <b>27</b>y + 81 = 0 (a −27, not +27); a sign error in the y-term.",
  "These coefficients do not arise from 13(3x−4y+7) = ±5(12x+5y−2).",
  "These are not multiples of the correct bisector equations."],
 sol:"(3x − 4y + 7)/√(9+16) = ±(12x + 5y − 2)/√(144+25) ⇒ 13(3x − 4y + 7) = ±5(12x + 5y − 2). + : 39x − 52y + 91 = 60x + 25y − 10 ⇒ 21x + 77y − 101 = 0. − : 39x − 52y + 91 = −60x − 25y + 10 ⇒ <b>99x − 27y + 81 = 0</b>."},

{id:54, lec:"L-6", blk:"Acute-angle bisector", topic:"Choosing the acute bisector",
 q:"The bisector of the acute angle between 2x − y + 4 = 0 and x − 2y − 1 = 0 is",
 opts:["x − y + 1 = 0", "x + y + 5 = 0", "3x + y − 2 = 0", "x − y − 1 = 0"],
 ans:0,
 why:[
  "Correct. With constants positive, a₁a₂ + b₁b₂ = (2)(−1) + (−1)(2) = −4 < 0, so + gives the acute bisector: <b>x − y + 1 = 0</b>.",
  "x + y + 5 = 0 is the <i>obtuse</i>-angle bisector (the − sign), perpendicular to the acute one.",
  "3x + y − 2 = 0 is not a bisector of this pair at all.",
  "x − y − 1 = 0 has the wrong constant; the acute bisector is x − y + 1 = 0."],
 sol:"Write as 2x − y + 4 = 0 and −x + 2y + 1 = 0 (constants +). a₁a₂ + b₁b₂ = (2)(−1) + (−1)(2) = −4 < 0 ⇒ take <b>+</b>: (2x − y + 4) = (−x + 2y + 1) ⇒ 3x − 3y + 3 = 0 ⇒ <b>x − y + 1 = 0</b>."},

{id:55, lec:"L-6", blk:"Origin-containing bisector", topic:"Bisector of the angle containing the origin",
 q:"The bisector of the angle containing the origin between 4x + 3y − 6 = 0 and 5x + 12y + 9 = 0 is",
 opts:["7x + 9y − 3 = 0", "7x + 9y + 3 = 0", "9x + 7y − 3 = 0", "77x + 99y + 33 = 0"],
 ans:0,
 why:[
  "Correct. Constants positive: −4x − 3y + 6 = 0 and 5x + 12y + 9 = 0; + sign ⇒ 77x + 99y − 33 = 0 ⇒ <b>7x + 9y − 3 = 0</b>.",
  "The constant is −3, not +3: 77x + 99y − 33 = 0 divides by 11 to 7x + 9y − 3 = 0.",
  "The x and y coefficients are 7 and 9 in that order, not swapped.",
  "This is the un-simplified form and also has the wrong sign on the constant."],
 sol:"Make constants positive: −4x − 3y + 6 = 0 and 5x + 12y + 9 = 0; origin ⇒ <b>+</b> sign. (−4x−3y+6)/13 = (5x+12y+9)/13·... ⇒ 13(−4x − 3y + 6) = 5(5x + 12y + 9) ⇒ −52x − 39y + 78 = 25x + 60y + 45 ⇒ 77x + 99y − 33 = 0 ⇒ <b>7x + 9y − 3 = 0</b>."},

{id:56, lec:"L-6", blk:"Bisector geometry", topic:"Relation between the two bisectors",
 q:"The two angle bisectors of a pair of intersecting lines are always",
 opts:[
  "perpendicular to each other",
  "parallel to each other",
  "parallel to the original lines",
  "coincident"],
 ans:0,
 why:[
  "Correct. The bisectors of the two supplementary angles are <b>perpendicular</b>.",
  "They meet at the intersection point, so they cannot be parallel.",
  "A bisector is never parallel to either original line (it splits the angle between them).",
  "They are two distinct lines, not one coincident line."],
 sol:"Adjacent angles between two lines are supplementary; their bisectors differ by 90°, so the two bisectors are always <b>perpendicular</b> to each other."},

{id:57, lec:"L-6", blk:"Acute vs obtuse rule", topic:"The a₁a₂ + b₁b₂ test",
 q:"After making both constant terms positive, you find a₁a₂ + b₁b₂ < 0. Then the bisector obtained with the <b>+</b> sign is the",
 opts:[
  "acute-angle bisector",
  "obtuse-angle bisector",
  "bisector containing the point (1, 1)",
  "line parallel to both original lines"],
 ans:0,
 why:[
  "Correct. With constants positive and a₁a₂ + b₁b₂ < 0, the <b>+</b> sign gives the acute-angle bisector.",
  "The − sign gives the obtuse bisector when a₁a₂ + b₁b₂ < 0; + gives the acute one.",
  "The point-containing rule is separate; the sign test here identifies acute vs obtuse.",
  "A bisector is never parallel to the original lines."],
 sol:"Rule: constants positive, then if a₁a₂ + b₁b₂ < 0 the <b>+</b> sign is the <b>acute</b> bisector; if &gt; 0 the − sign is the acute one."},

{id:58, lec:"L-6", blk:"Origin-containing bisector", topic:"Which sign gives the origin bisector",
 q:"To find the bisector of the angle containing the origin, you first make both constants positive and then take the sign",
 opts:["+ (plus)", "− (minus)", "whichever makes the slope positive", "either, they give the same line"],
 ans:0,
 why:[
  "Correct. With both constants written positive, the origin-containing bisector is the <b>+</b> branch.",
  "The − branch gives the bisector of the angle <i>not</i> containing the origin.",
  "The choice is fixed by the sign rule, not by the resulting slope.",
  "The two signs give perpendicular, distinct lines."],
 sol:"Arrange a₁x + b₁y + c₁ and a₂x + b₂y + c₂ with <b>c₁, c₂ &gt; 0</b>; the bisector of the angle containing the origin is the one with the <b>+</b> sign."},

{id:59, lec:"L-6", blk:"Circumcentre by slopes", topic:"Circumcentre from perpendicular bisectors",
 q:"The circumcentre of the triangle with vertices A(5, −1), B(−1, 5), C(6, 6) is",
 opts:["(23/8, 23/8)", "(10/3, 10/3)", "(23/8, 8/23)", "(0, 0)"],
 ans:0,
 why:[
  "Correct. Solving 7α + β = 23 and α + 7β = 23 (equal distances) gives α = β = <b>23/8</b>.",
  "(10/3, 10/3) is the centroid (A+B+C)/3, not the circumcentre.",
  "By symmetry α = β, so the second coordinate is 23/8, not 8/23.",
  "The origin is equidistant from none of the three vertices here."],
 sol:"Circumcentre O(α,β) is equidistant from the vertices; perpendicular bisectors give 7α + β = 23 and α + 7β = 23. Subtracting: 6α − 6β = 0 ⇒ α = β; then 8α = 23 ⇒ α = β = <b>23/8</b> ⇒ (23/8, 23/8)."},

{id:60, lec:"L-6", blk:"Centres by slopes", topic:"Orthocentre condition",
 q:"In finding the orthocentre by slopes, the defining relation for an altitude is that the slope of the altitude times the slope of the opposite side equals",
 opts:["−1", "+1", "0", "the slope of the third side"],
 ans:0,
 why:[
  "Correct. An altitude is <b>perpendicular</b> to the opposite side, so the slope product is −1.",
  "A product of +1 would mean the lines are reflections across a 45° line, not perpendicular.",
  "Product 0 would require one slope to be 0; perpendicularity needs the product −1.",
  "Perpendicularity is a fixed condition (product −1), unrelated to the third side's slope."],
 sol:"An altitude from a vertex is perpendicular to the opposite side, so (slope of altitude)·(slope of opposite side) = <b>−1</b>. Solving two such equations locates the orthocentre."},

{id:61, lec:"L-6", blk:"Point-containing bisector", topic:"Bisector containing a chosen point",
 q:"To select the bisector of the angle containing a point P(x₁, y₁), after arranging both constants to the same sign you",
 opts:[
  "check the signs of a₁x₁ + b₁y₁ + c₁ and a₂x₁ + b₂y₁ + c₂, and take + if they match, − if they differ",
  "always take the + sign",
  "take the sign that makes p larger",
  "take the bisector with the smaller slope"],
 ans:0,
 why:[
  "Correct. If the two expressions evaluated at P share a sign, the + bisector contains P; if opposite, the − one does.",
  "The + sign only works when P happens to be on the same side as the origin's reference; the test is the sign-matching rule.",
  "There is no quantity p here to maximise; the choice is by sign-matching at P.",
  "Slope size does not determine which bisector contains a given point."],
 sol:"Arrange both constants to the same sign; evaluate a₁x₁ + b₁y₁ + c₁ and a₂x₁ + b₂y₁ + c₂ at P. Signs <b>match</b> ⇒ take + ; signs <b>differ</b> ⇒ take − ."},

{id:62, lec:"L-6", blk:"Both bisectors", topic:"Checking perpendicularity of the bisector pair",
 q:"The two bisectors 21x + 77y − 101 = 0 and 99x − 27y + 81 = 0 of a line pair should be perpendicular. Their slope product is",
 opts:["−1", "+1", "−21/99", "0"],
 ans:0,
 why:[
  "Correct. slopes −21/77 = −3/11 and 99/27 = 11/3; product (−3/11)(11/3) = <b>−1</b> ✓.",
  "A product of +1 would contradict the known perpendicularity of bisectors.",
  "−21/99 is not even a slope here; the slopes are −3/11 and 11/3.",
  "A product 0 would need one slope to be 0, which neither is."],
 sol:"Slope of 21x + 77y − 101 = 0 is −21/77 = −3/11; slope of 99x − 27y + 81 = 0 is 99/27 = 11/3. Product = (−3/11)(11/3) = <b>−1</b>, confirming the bisectors are perpendicular."},

{id:63, lec:"L-6", blk:"Centres by slopes", topic:"Circumradius after circumcentre",
 q:"With circumcentre (23/8, 23/8), the circumradius of the triangle A(5, −1), B(−1, 5), C(6, 6) is",
 opts:["(25√2)/8", "25/8", "(23√2)/8", "25/4"],
 ans:0,
 why:[
  "Correct. R = OC = √[(23/8 − 6)² + (23/8 − 6)²] = √[2·(25/8)²] = <b>(25√2)/8</b>.",
  "25/8 is |23/8 − 6| alone, missing the √2 from combining both equal coordinate gaps.",
  "The gap is 23/8 − 48/8 = −25/8, so the magnitude is 25, not 23.",
  "25/4 drops the √2 and halves the denominator incorrectly."],
 sol:"R = OC, with O = (23/8, 23/8), C = (6, 6). 23/8 − 6 = −25/8, so R = √[(−25/8)² + (−25/8)²] = √2·(25/8) = <b>(25√2)/8</b>."}

];

/* ---- timer t: steps = count of '='/'⇒' in plain-text sol;
       180 if steps≥12 and plain q≥80 chars; 60 if steps≤2; else 90 ---- */
QUIZ.forEach(q => {
  const plain = s => String(s).replace(/<[^>]+>/g, "");
  const steps = (plain(q.sol).match(/=|⇒/g) || []).length;
  const qlen = plain(q.q).length;
  q.t = (steps >= 12 && qlen >= 80) ? 180 : (steps <= 2 ? 60 : 90);
});

/* ============================================================
   ENGINE  v2 — one question at a time · soft per-question timer ·
   downloadable result page.  Identical across chapters.
   ============================================================ */

module.exports = {META, LECTURES, QUIZ};
