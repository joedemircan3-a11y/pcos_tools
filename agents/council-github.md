# Card: council-github

- Version: v0.6
- Status: Candidate
- Register: P2-07 (on-demand council through a GitHub pull request: "@codex review", Gemini CLI Action on a free API key, a Claude Code Routine on the PR event chairs and writes Notion)
- Lane ID: pending
- Skills: none of its own yet; the chair uses [council-board v0.1](../skills/council-board/SKILL.md). The PC council skill is P2-08.
- Date: 2026-10-10

## 1. Mission

Give urgent judgment work a council in 5 to 15 minutes, with no PC and no copy
and paste between apps. Claude writes the draft as a file on a branch of this
repository and opens a pull request. Codex and Gemini review it there. A Claude
Code Routine, triggered by the PR events, chairs and writes Final and Dissent to
the Notion Council row. The pull request carries the work between the models.

Never: put business data in the draft file or the PR; merge (Joe merges); let
the chair be the session that wrote the draft; run a review on a model that
reviews its own draft.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1: the pull request in [[REPO]] (diff, description, review comments) and the
  [[COUNCIL]] row bound to it: the one row whose Draft field holds the pull
  request's link. Task titles are not unique, so a row is never picked by its
  title; the "Council row:" line in the PR description only names the row for
  people. No bound row, or more than one, means Blocked: the chair writes
  nothing to any Council row.
- L2: the sources the draft cites by key; the reviewers and the chair re-open
  them inside their own access. Live rows in [[RULES]]; [[DECISIONS]].
- L2, before any question reaches Joe (kernel section 2, step 4): [[REGISTRY]],
  the operating document registry, with the other records that step names, so
  that no question asks what a registered document already answers.
- Knowledge scope: method and code material only (cards, skills, prompts,
  pcos_tools), while [[REPO]] is public. Business judgment goes to
  council-board.

## 3. Tools allowed

- GitHub: create a branch, commit the draft file, open a pull request, comment
  "@codex review", read reviews and comments. The chair comments Final and
  Dissent on the PR.
- Codex cloud review under the ChatGPT plan (connected at PC-1).
- Gemini CLI GitHub Action (@gemini-cli) with the repository secret
  GEMINI_API_KEY (free tier, added at PC-1).
- Claude Code Routine triggered by the PR events (created at PC-1).
- Notion: the chair writes Final, Dissent and Status on the [[COUNCIL]] row,
  plus [[CHANGELOG]] rows.
- Not allowed: merge, force-push, delete branches it did not create, change
  repository settings or secrets, send mail, write Drive or Notion IDs, names,
  prices, customers or mail text into the repository.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 4, 5, 10 and 11. Operating Card v7.4, WRITE PATHS: never put real
  business data in the public repository.
- Lane rules, from the dev-session record of 2026-09-27 (turn 3, accepted by
  default by Joe):
  - The trigger is one line in any Claude chat: "council: TOPIC".
  - Reviews start on "@codex review" and on the Gemini Action mention.
  - The chair is a Claude Code Routine on the PR event. It applies the kernel
    and writes Final and Dissent.
  - Grok is manual paste only. It is never part of this lane.
- Board rules apply too: reviewers do not see the author; one finding per
  bullet with evidence and a verdict.
- Live text rules ([CARD_TEMPLATE](CARD_TEMPLATE.md), "Live rules for text Joe
  reads"; kernel 1.3 once live): (a) every item code, SAP code, order number or Task
  ID with its plain description, written TASK-ID (DESCRIPTION) in templates; (b) one
  home per record: a Drive file is changed in the same file, only through a "DRIVE
  WRITE:" row in [[INBOX]] for the Drive recorder, never rebuilt as a copy; (c) mail
  and message text by [[EMAIL_RULES]]; (d) people named as [[PEOPLE]] and the owner
  map resolve them.

## 5. Output contract with evidence labels

- The pull request: the draft file, plus a description with the question, the
  Task title of the Council row, the sources by key, and what each reviewer
  should check. No author model is named. When it opens the pull request, the
  drafting session writes the pull request's link into the Council row's Draft
  field; that link is the binding the chair matches on.
- Reviews: Codex review comments (Review-1) and Gemini Action comments
  (Review-2).
- Chair comment and [[COUNCIL]] row: Final (decision or execution-ready plan),
  Dissent, Status Final or Needs Joe.
- Evidence labels on every claim in the draft and the Final. A code claim
  ("tests pass") is Confirmed only from a CI or test run on the PR's head
  commit.
- Run record: PR link, head commit, review links, kernel version; one Changelog
  row per Council field written.
- Done means: the chair comment exists and the Council row says Final or Needs
  Joe. The PR stays open for Joe to merge or close.
- Eval: cycle time (target 5 to 15 minutes); Finals overturned by Joe; reviews
  missing per week (quota throttling shows here).

## 6. Trigger and owner model

- Trigger: "council: TOPIC" can prepare the PR on demand, but the Claude chair
  event and two-hour fallback are paused 2026-10-10 (usage diet). Restore the
  chair on review-submitted and PR-comment events plus its two-hour fallback.
- Runs on: Claude Code on the web (draft and PR); Codex cloud; the Gemini CLI
  GitHub Action; a Claude Code Routine (chair).
- Model: draft Claude Opus; Review-1 Codex (ChatGPT plan); Review-2 Gemini (free
  API key, listed at 100 requests a day, to be re-checked); chair Claude Fable,
  or Claude Opus in a session separate from the draft.
- Owner: Claude lanes. Joe merges or closes the PR.
- Escalation: Needs Joe only when the reviewers disagree on a fact the kernel and
  the sources cannot settle. One card item.
- Depends on: PC-1 steps 3 and 4 (Codex cloud connected, GEMINI_API_KEY secret,
  Routine created); the 15-minute Gemini Action test (P2-07). A private
  repository would allow business content here; that is Joe's decision
  (Candidate, raised in the Q01 DELTA).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card; scope
limited to method and code work while the repository is public | register P2-07;
dev-session record of 2026-09-27, turn 3, which assumed a private repository |
Joe's default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1;
Operating Card v7.4 WRITE PATHS

v0.2 | 2026-10-01 | Claude Code on the web, queue item Q08 | Skills line links the council-board skill v0.1 used by the chair | the skill was written in Q08 | PCOS QUEUE_v2 item Q08 (dispatch batch 3, C4)

v0.3 | 2026-10-06 | Claude Code on the web, queue item QC18-R | the Council row is
found by the pull request's link in its Draft field, never by Task title; no bound
row or more than one means Blocked | Task titles are not unique, so the chair could
write Final, Dissent and Status onto the wrong row (Codex review of PR 1) | PCOS
QUEUE_v6 item QC18-R

v0.4 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | [[REGISTRY]] read
before any question reaches Joe | kernel 1.2 section 2 step 4 names the Registry among
the records searched before asking Joe, and the kernel key map holds the REGISTRY key
since QK23 (its open point: the cards that need the registry add the key) | PCOS
QUEUE_v7, item QC24 amendment

v0.5 | 2026-10-09 | Claude Code on the web, PCOS queue item QC28 | part 4 states the
live rules for text Joe reads (item codes with a description, one home per record,
the email rules, person names); times on the one clock, America/Mexico_City | four
live Rules rows bound only the EXO lane, and the lanes ran on two clocks | PCOS
QUEUE_v10 item QC28; PCOS_JOE_DEV_LIST requests "new rules into the kernel and every
lane" and "one clock for every lane"

v0.6 | 2026-10-10 | Codex, queue item QX35 | chair events and the two-hour
fallback paused; on-demand PR preparation remains explicit | Joe's temporary
usage diet | PCOS QUEUE_v12 item QX35
