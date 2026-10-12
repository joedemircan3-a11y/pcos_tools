# DELTA QX40 — Matamoros clock and direct evening commitments

Confirmed repository change, authorized by Joe's QX40 instruction on 2026-10-11. Base: main e863938ea5d358d49fb3c3ee2538a938fc1215fc. Prior QC28 clock is superseded in current instructions; historical change notes keep their original zone.

| Lane / routine file | Old time zone | New time zone | State / clock scope |
| --- | --- | --- | --- |
| commitments-backfill (`routines/commitments-backfill.md`) | America/Mexico_City | America/Matamoros | Manual only; no recurring trigger |
| commitments (`routines/commitments.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| council-board-chair (`routines/council-board-chair.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| council-board-draft (`routines/council-board-draft.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| council-board-review-2 (`routines/council-board-review-2.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| council-github-chair (`routines/council-github-chair.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| exo (`routines/exo.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| intake-email (`routines/intake-email.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| knowledge-extract (`routines/knowledge-extract.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| knowledge-review-2 (`routines/knowledge-review-2.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| L1-brief (`routines/L1-brief.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| L2-render (`routines/L2-render.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| L3-health (`routines/L3-health.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| L4-weekly (`routines/L4-weekly.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| ledger-backtest (`routines/ledger-backtest.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| prediction-ledger (`routines/prediction-ledger.md`) | America/Mexico_City | America/Matamoros | Restore schedule; stays off |
| retro (`routines/retro.md`) | America/Mexico_City | America/Matamoros | Active trigger |
| L5 CAL | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| PCOS hub sync | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| Drive recorder (Claude side) | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| L6 07-SAP-01 | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| G1 Project Watch | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| G2 Weekly leadership page | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| council-board Review-1 | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| knowledge-review Review-1 | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| N1 Decision processor | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| N2 Hub hygiene | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| N3 Inbox mail | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| X1 Codex Watchdog | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |
| checker (L7) | America/Mexico_City (prior index convention) | America/Matamoros (new index convention) | No routine file; installed clock unverified, or no schedule of its own |

Every routine's active or Restore cron uses CRON_TZ=America/Matamoros. The QX35 usage diet remains in force: paused/uninstalled lanes stay off, manual backfill stays manual, and no wall time or cron frequency changes. Lanes without routine files are listed under the inherited index convention only; this PR cannot verify or change their installed timers.

Retro reads open Commitments rows itself at 18:53, refreshes evidence and dates, applies commitments sections 4–8, and selects at most two eligible rows more than 14 days overdue, oldest date first. It reserves those places within five total items. No Card mark, noon run, 18:40 run or weekday execution is a prerequisite. Answers, skip handling, Registry checks and checker gates remain required.

Validation: clock and usage-diet tests pin Matamoros, reject Mexico City, and retain paused/manual states. Retro contract tests pin direct reads, evidence refresh, eligibility, suppressions, skips, ordering and both card caps. Full pytest result and Codex review are recorded in the PR and DONE receipt after merge.

Next: review and merge this PR; the authorized installer applies the new timezone and retro prompt to installed routines, including paused Restore schedules. Installed timers and private kernel/Lanes records were not edited by this code task.

QX40 | routine/card clocks changed and retro selects open rows directly | merge, then apply installed routine clocks and retro prompt | Confirmed for repository; Needs Source Check for installed timers

Review round 1 fixes: the checker now accepts direct unmarked commitments only after source checks; retro reads and applies changed mail dates by commitments section 3 before ranking and may persist Linked task discovered in evidence refresh. Four plain-language clock references now name Matamoros. Regression checks cover each finding. No Worklist write or mail send is authorized.
