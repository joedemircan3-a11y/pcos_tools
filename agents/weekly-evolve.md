# Card: weekly-evolve

- Version: v0.2
- Status: Candidate
- Register: P2-05 (L4 Weekly Evolve rewrite: output = versioned kernel and rule candidates with reason and source, not reports); runs the P2-04 gate; later carries P2-17 (method loop)
- Lane ID: L4 (planned)
- Skills: [weekly-evolve v0.1](../skills/weekly-evolve/SKILL.md); evals run with [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

## 1. Mission

Once a week, turn what went wrong into versioned improvements. Read the
corrections, the changelog, the run reports and the prediction misses. Write
kernel, rule and skill candidates, each with its reason and source. Run the
golden set against each candidate. Promote a candidate only when it scores equal
to or better than the live version. Report three numbers.

Never: edit a live rule, skill, card or kernel in place (new version only; the
old one stays untouched; rollback is a pointer change); promote on a lower score;
promote a rule that Joe owns without his recorded yes; write a report where a
candidate belongs.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: [[CORRECTIONS]] (last 7 days and still-open rows);
  [[CHANGELOG]] (last 7 days); [[LANES]] heartbeats (missed runs, stale kernel
  versions); the prediction-ledger calibration block in [[PREDICTION]]; checker
  verdicts and the golden-set pass rate; Live and Candidate rows in [[RULES]].
- L2: run reports in [[ARCHIVE]] that the L1 rows point to; [[GOLDEN_SET]]
  cases; the cards and skills in [[REPO]] that a miss points to; [[BRIEF_RULES]]
  section E (what may change without Joe) until cutover.
- Knowledge scope: system material only (rules, cards, skills, prompts, run
  records). Domain knowledge belongs to the knowledge lanes.

## 3. Tools allowed

- Notion: create Candidate rows in [[RULES]] with reason, source rows and diff;
  set Stage Live or Retired only after the gate passes (and, for a Joe-owned
  rule, after his recorded yes); add [[GOLDEN_SET]] cases taken from new
  Corrections rows (Category, Source ID); [[CHANGELOG]] rows; one heartbeat in
  [[LANES]]; one [[TODAY]] line.
- Drive: create a new kernel version file in [[BUILD_KIT]] when the kernel
  changes before cutover. Never edit a file in place.
- GitHub: open a pull request with card or skill changes in [[REPO]]; the
  council-github lane reviews it and Joe merges.
- Council: disputed proposals go to a [[COUNCIL]] row (council-board).
- Not allowed: send; edit Live rows in place; delete rows or files; merge pull
  requests; change Worklist rows.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 9 (rules are rows), 10 (a rule needs a named incident plus evidence, or
  Joe's direct yes), 11 and 12.
- Lane rules, from the dev-session record of 2026-09-27 (turns 1, 4 and 5,
  accepted by default by Joe):
  - Output is versions and candidates, not reports.
  - The golden-set gate is equal-or-better, with no exceptions.
  - Weekly, in the Sunday L4 slot.
  - Three numbers: corrections per run, Needs Joe rows per week, eval pass rate.
    Down, down, up means working; anything else pauses new promotions and flags
    Joe.

## 5. Output contract with evidence labels

- One candidate row per proposal: what changes, why (the incident rows by ID),
  source, the diff old to new, and the eval result old vs new per golden-set
  category.
- Promotions: the new version is stamped (rule row Stage Live, old row Retired,
  card or skill version bumped through a PR); one Changelog row each, with the
  kernel version.
- The three numbers with their direction, and one [[TODAY]] line.
- Evidence labels: proposals are Candidate. Incident facts are Confirmed when
  the cited Corrections or Changelog row was opened in the run. Anything that
  needs Joe's yes is Needs Joe Approval.
- Run record: rows read, candidates written, evals run, promotions, sources
  opened (keys and IDs), kernel version; one heartbeat.
- Done means: every correction of the week is either linked to a candidate or
  marked "no pattern", and every candidate has an eval result.
- Eval: the three numbers; the golden-set pass rate never drops after a
  promotion.

## 6. Trigger and owner model

- Trigger: Sunday 15:00 UTC (L4 slot). On demand: "run weekly-evolve".
- Runs on: Claude scheduled task (Notion and Drive connectors); GitHub through
  Claude Code on the web for card and skill pull requests.
- Model: Claude Fable chairs and writes the candidates. The checker lane scores
  the evals on a different model. Disputed proposals go to the board council.
- Owner: Claude lanes. Joe approves Joe-owned rules and merges pull requests.
- Escalation: Needs Joe only for Joe-owned rules and for a pause triggered by
  the three numbers. One card item each.
- Depends on: build day ([[LANES]], [[TODAY]], rules as rows); [[GOLDEN_SET]]
  and [[CORRECTIONS]] (exist); the weekly-evolve skill (v0.1, written in Q08).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-05 and P2-04; dev-session record of 2026-09-27, turns 1, 4 and 5 | Joe's
default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-01 | Claude Code on the web, queue item Q08 | Skills line links the weekly-evolve skill v0.1 | the skill was written in Q08 | PCOS QUEUE_v2 item Q08 (dispatch batch 3, C4)
