---
name: weekly-evolve
description: Turn a week of PCOS corrections and misses into versioned improvements. Use in the Sunday L4 pass, or when asked to propose a rule, kernel, card or skill change. Reads Corrections, Changelog, lane heartbeats, run reports, prediction misses and checker results; writes candidates with reason, source and diff; adds new golden-set cases; runs the golden set old against new; promotes only on equal-or-better; reports the three weekly numbers.
compatibility: Needs the PCOS Notion hub (Corrections, Changelog, Rules, Golden Set, Prediction, Lanes, Today) and Drive read for run reports; GitHub access to this repository for card and skill pull requests.
metadata:
  version: "0.1"
  status: Candidate
  register: P2-05
  kernel: "1.0"
  card: agents/weekly-evolve.md
---

# Weekly evolve

Output is versions and candidates, not reports. Nothing live is edited in place:
a change is a new version, the old version stays untouched, and rollback is a
pointer change.

Sources are named by key, written `[[KEY]]` (defined in `agents/INPUTS.md`, IDs
in the private map named there).

## 1. Collect the week

- [[CORRECTIONS]]: rows from the last 7 days, and older rows still open.
- [[CHANGELOG]]: rows from the last 7 days, plus any REASON-MISSING flags.
- [[LANES]]: missed runs and runs on a stale kernel version.
- The calibration block from the prediction-ledger lane ([[PREDICTION]]) and the
  checker's verdicts and golden-set scores.
- Run reports in [[ARCHIVE]] that these rows point to.

For each correction, note: the lane, the output, Joe's correction (verbatim),
and the line that caused the miss (a Rules row, a kernel section, a skill or
card line), if one can be found.

## 2. Group into patterns

Group corrections by cause: missing source, wrong route, wrong owner, wrong
label, re-asked question, style, rule misapplied, stale rule, missing rule. One
named incident with evidence is enough for a candidate (Law 10). Corrections
with no findable cause are marked "no pattern" and stay listed.

## 3. Write candidates

One candidate per proposed change:

| Field | Content |
| --- | --- |
| Object | Rules row number, kernel section, or the card or skill file and line |
| Current | The live text, verbatim |
| Proposed | The new text |
| Reason | The incident rows (Corrections or Changelog IDs) and what went wrong |
| Source | Joe's words with date, the rule, or the source document |
| Class | AUTO (may change without Joe: [[BRIEF_RULES]] section E until cutover, then the kernel) or JOE (needs his recorded yes) |
| Expected effect | Which golden-set categories should improve |

Where each candidate goes:

- Rules: a new Candidate row in [[RULES]].
- Kernel: a new version file in [[BUILD_KIT]] until build day, then the kernel
  page's candidate section.
- Cards and skills: a pull request in [[REPO]] with the version bumped and a
  change-note line. The council-github lane reviews it, and Joe merges.

## 4. Grow the golden set

For each correction of the week that is not yet a case, add a [[GOLDEN_SET]] row:
the next free Case ID, Date, Input (as short as possible), Wrong output, Joe's
correction (verbatim where available), the rule it implies, Source ID and
Category (routing, drafting, pricing, sources, re-asking, formatting). A case
without a verifiable source goes in with Category Needs Source Check. It is
never dropped.

## 5. Evaluate old against new

Run the checker's golden-set run twice: once with the live version, once with the
candidate. Record the passes per category for each.

The gate is equal-or-better, with no exceptions:

1. The overall pass rate of the candidate is equal to or higher than live, and
2. no category's pass rate is lower than live.

Needs Source Check cases are listed and not scored.

## 6. Promote or hold

- AUTO class and gate passed: promote. For a rule: the new row becomes Live and
  the old row Retired. For the kernel: the version number goes up. For a card or
  skill: the pull request is marked ready for Joe's merge. Write one Changelog
  row per promotion: what, why, authority, before and after, kernel version.
- JOE class and gate passed: one card item for Joe in the next EXO slot, with
  the diff in plain words, the reason and the eval result. Default: keep the
  current version. Nothing changes on silence.
- Gate failed: the candidate stays Candidate, with its failing cases listed.
- Rollback: if a version promoted last week shows a lower pass rate, or new
  corrections trace to it, point back to the previous version (as a change with
  its reason) and reopen the candidate.

## 7. The three numbers

| Number | How |
| --- | --- |
| Corrections per run | Corrections this week / lane runs this week |
| Needs Joe rows per week | Rows set to Needs Joe this week, across lanes |
| Eval pass rate | The live version's golden-set pass rate after this run's promotions |

Compare with last week. Down, down, up means working. Anything else: no
promotions next week except rollbacks, and one [[TODAY]] line plus one card item
flag it to Joe.

## 8. Record

One [[TODAY]] line with the three numbers and the promotions. One Changelog row
per change. One heartbeat in [[LANES]].

## Never

- Edit a Live rule, the kernel, a card or a skill in place.
- Promote when any category drops, or promote a JOE-class change without Joe's
  recorded yes.
- Delete a golden-set case or a correction.
- Write a report where a candidate belongs.
