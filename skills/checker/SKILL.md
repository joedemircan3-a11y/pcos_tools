---
name: checker
description: Check a PCOS lane output before its row closes or it reaches Joe. Use when a lane hands over a mail draft, routing decision, row change, DELTA, question card, prediction, pricing preparation, research file, knowledge claim, council Final, rule candidate or repository change, or when asked to check one. Opens the sources the job type requires, applies its rules, verifies every evidence label and returns Accept, Fix or Reject with one finding per line.
compatibility: Needs read access to the sources the generating lane used (Google Drive, the PCOS Notion hub, Outlook through the Microsoft 365 connector) and must run on a different model from the generator.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-03
  kernel: "1.0"
  card: agents/checker.md
---

# Checker

The generator never checks its own work. Run this skill on a different model
from the one that produced the output (see the checker card,
`agents/checker.md`).

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`).
Resolve each key to its ID through the private ID map named there. A key that
does not resolve makes that check Blocked. Do not search for a substitute.

## Inputs

1. The output: the draft, row, file, card or diff.
2. Its run record: the job type, the kernel version the generator loaded, and
   the sources the generator opened, with keys and IDs.

## Procedure

1. **Kernel.** If the generator loaded an older kernel version than the current
   one, stop. Verdict Reject, finding "stale kernel".
2. **Job type.** Pick the checklist for the job type in
   [references/checklists.md](references/checklists.md). If the output fits no
   job type, Reject with "unknown job type". Do not improvise a checklist.
3. **Open the sources yourself.** Open every source the checklist marks
   required, now, in this run. Record each key and ID. A required source that
   the generator did not open is a finding, even when the output happens to be
   right.
4. **Run the checks** in checklist order. Write one line per check: PASS or FAIL,
   the evidence (key, ID, and the field, line or message read) and, for a FAIL,
   the fix.
5. **Labels.** Every claim in the output carries one of the six Law 4 labels, and
   the label matches what you found:
   - Confirmed: a source opened in this run states it. For mail, the terminal
     message of the thread.
   - Candidate: inference, plan, prediction, proposal or draft.
   - Needs Source Check: a source exists but was not opened, or does not state
     it.
   - Needs Thread Check: the claim rests on mail and the terminal message was
     not read.
   - Needs Joe Approval: anything external or committing (send, price, payment,
     vendor term, canon change).
   - Blocked: the source could not be opened.
   A missing label, or Confirmed without an opened source, is a FAIL.
6. **Re-ask.** Compare every question the output puts to Joe with the decided
   rows in [[DECISIONS]], Joe's replies in the thread, and [[MAIL_SENT]]. A
   match is a FAIL that names the row or message that already answers it.
7. **Hard stops.** Reject when the output does any of these: sends, pays,
   commits a price, negotiates with a vendor or promotes canon; deletes, or
   renames, moves or trashes a file the lane did not create; mints a Task ID
   outside a closeout; puts Room 10 or personal content into a business object;
   copies a credential; writes a Drive or Notion ID, a person's name, a price, a
   customer or mail text into the public repository.
8. **Verdict.**
   - Accept: every check PASS.
   - Fix: one or more FAILs that the generator can repair from sources. List the
     fix for each. The generator re-runs and you check again, up to 5 rounds.
     After round 5 the open findings go to Joe as one card item.
   - Reject: a hard stop, a stale kernel, an unknown job type, or an output
     built on a source that does not exist.

## Output

Write this block on the output row (field or comment) and add one Changelog row:
what was checked, the verdict, why, and the kernel version.

```
CHECK job-type | verdict Accept, Fix or Reject | kernel VERSION | round N of 5
Sources opened: [[KEY]] ID; [[KEY]] ID; ...
1. CHECK NAME | PASS or FAIL | evidence: KEY, ID, field or line | fix: WHAT TO CHANGE
2. ...
Labels: N claims, N correct, N wrong (list the wrong ones)
Re-ask: none, or QUESTION already answered in KEY, ID
```

## Golden-set runs (weekly)

Run before the weekly-evolve lane, on [[GOLDEN_SET]]. There are two runs,
because they test two different things: the lanes' outputs, and this checker.

### Lane run: scores a lane version

1. For each case, give the case's Input to the version under test (live or
   candidate) of the lane its Category belongs to.
2. Run this skill on the new output, with one added check: the output satisfies
   Joe's correction (it does what the correction asks and follows the rule it
   implies) and does not repeat the defect of the case's Wrong output. Open the
   case's Source ID when the correction is unclear.
3. The case passes when that check is PASS and the skill's overall verdict on
   the output is Accept. A version that no longer makes the mistake passes, even
   though the checker then has nothing to raise; a version that fixes the old
   defect but fails another check or hits a hard stop does not.

### Checker run: scores a checker version

The run has two halves, so a checker that fails everything cannot score well.

1. Defect half: for each case, run the checker version under test (live or
   candidate) on the case's Wrong output, with its Input. It passes when the
   checker raises the defect that Joe's correction names (a FAIL on the
   matching check) and does not Accept.
2. Clean half: run the same version on known-good outputs of the same
   categories: a case's corrected output where Joe's correction is a full
   corrected version, and lane outputs from the last 4 weeks that Joe used
   unedited (Candidate output scored "used unedited" in [[PREDICTION]], with no
   [[CORRECTIONS]] row). Each passes when the checker gives Accept.

### Scores

- Score each run per Category (routing, drafting, pricing, sources, re-asking,
  formatting) = passed cases / cases. Cases with Category Needs Source Check
  are listed but not scored. The two runs' scores are never added together.
- In the checker run, score the defect half and the clean half separately. For
  the gate, each half counts as its own category, so a candidate whose clean
  half drops fails, however well it finds defects.
- The weekly-evolve gate compares live and candidate with the lane run, except
  for a change to this skill or its checklists, which it compares with the
  checker run.
- Hand the scores and the failing case IDs of both runs to the weekly-evolve
  lane.

## Never

- Check output your model produced in the same session.
- Rewrite the output. Findings only; the generator fixes.
- Accept on the generator's word. Open the sources yourself.
- Open sources outside the generator card's knowledge scope.
