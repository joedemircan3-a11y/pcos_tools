# Card: checker

- Version: v0.2
- Status: Candidate
- Register: P2-03 (L7 checker lane: generator/checker split, Claude-internal council, checklist per job type); runs the P2-04 golden-set eval
- Lane ID: L7 (planned)
- Skills: [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

## 1. Mission

Check every lane output before its row closes or it reaches Joe. Three questions:
were the required sources opened, do the rules for that job type hold, does every
claim carry the right evidence label. Answer with Accept, Fix or Reject and one
finding per line.

Never: check output that the same model produced in the same session; rewrite
the output (findings only; the generator fixes); accept without opening the
sources itself; pass anything that sends, pays, commits a price, negotiates with
a vendor, promotes canon or deletes.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, per output: the output itself and its run record (job type, kernel
  version, the sources the generator opened with keys and IDs); the checklist
  for the job type in the skill's `references/checklists.md`.
- L2, per checklist: every source the checklist marks required, opened again by
  the checker. Typical ones: the thread's terminal message in [[MAIL_INBOX]],
  [[MAIL_ROUTED]] or [[MAIL_SENT]]; the task row in [[WORKLIST]]; the Rules rows
  that apply in [[RULES]]; [[DECISIONS]] for re-asked questions; [[CORRECTIONS]]
  rows with the same pattern; [[CANON]] until rules are rows.
- L2, weekly eval: [[GOLDEN_SET]].
- Knowledge scope: exactly the generator card's scope. The checker never widens
  a lane's scope.

## 3. Tools allowed

- Read: the connectors the generator used, read-only.
- Notion: write the verdict block on the output row (verdict field or a row
  comment); one [[CHANGELOG]] row per verdict; one heartbeat in [[LANES]] when
  it runs as its own pass.
- Claude-internal council (dev-session mechanism C): subagents on different
  Claude models in one session. Opus generates, Sonnet checks, Fable chairs a
  disagreement.
- Not allowed: edit the output; set any status other than the verdict; send or
  draft mail; mint IDs; open sources outside the generator's scope.

## 4. Rules and kernel version

- Kernel 1.0. A generator that ran on an older kernel version gets Reject with
  the finding "stale kernel". The live-rules fallback is in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3, 4, 5, 8, 10, 11 and 12. Joe's preferences in the kernel: never
  re-ask; drafts on the original thread; correction-email form.
- Lane rules, from the dev-session record of 2026-09-27 (turns 1 and 2, accepted
  by default):
  - Generator and checker are different models; the judge is never the author.
  - A row does not close until its checklist passes.
  - A question that matches an answered one is rejected.
  - Fix loops stop after 5 rounds (the iteration cap from the loop-until-verified
    pattern). Open findings then go to Joe as one card item.

## 5. Output contract with evidence labels

- Verdict block (format in the skill): verdict Accept, Fix or Reject; job type;
  kernel version; round number; the sources the checker opened (keys and IDs);
  one finding per line with check, PASS or FAIL, evidence and the required fix.
- Evidence labels: the checker verifies labels; it does not add new claims.
  Confirmed needs a source opened in the run that states the claim. Candidate is
  for inference. Needs Thread Check applies when the terminal message was not
  read, Needs Source Check when the source was not opened, Needs Joe Approval
  for anything external, Blocked when a source could not be opened. A missing or
  wrong label is a FAIL.
- Run record: outputs checked, verdicts, rounds, sources opened, kernel version;
  one Changelog row per verdict.
- Done means: every output handed over in the run has a verdict. A Reject, or a
  sixth round, becomes one Needs Joe card item with the open findings.
- Eval: the weekly [[GOLDEN_SET]] runs in the skill. The lane run scores each
  lane's output: it passes when the output satisfies Joe's correction. The
  checker run scores this lane: it passes when the checker raises the defect in
  the case's Wrong output. Pass rates per category (routing, drafting, pricing,
  sources, re-asking, formatting) go to the weekly-evolve lane, one set per run.

## 6. Trigger and owner model

- Trigger: an output handed over by any lane (end of the generator's run, or a
  row set ready for check). Weekly golden-set runs on Sunday before the
  weekly-evolve lane.
- Runs on: inside the generating lane's session as a subagent on a different
  model (routine lanes), or as its own Claude scheduled pass for queued outputs.
- Model: Claude Sonnet checks Claude Opus output; Claude Opus checks GPT or
  Sonnet output; Claude Fable chairs disagreements.
- Owner: Claude lanes. The checklists change only through weekly-evolve: new
  version, golden-set gate.
- Escalation: Needs Joe only after 5 Fix rounds, or on a Reject that needs a
  decision. One card item each.
- Depends on: build day (kernel page, [[LANES]]); [[GOLDEN_SET]] (exists).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card | register
P2-03; design in the dev-session record of 2026-09-27, turns 1 and 2 | Joe's
default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1

v0.2 | 2026-10-06 | Claude Code on the web, queue item QC18 | Eval: the golden-set
lane run scores whether the lane's output satisfies Joe's correction; the checker
run scores the checker separately | the old criterion passed a version that kept
the defect and failed one that fixed it (Codex review of PR 1) | PCOS QUEUE_v4
item QC18
