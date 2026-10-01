# Card: intake-email

- Version: v0.1
- Status: Candidate
- Register: P2-09 (team access Door 1: Outlook intake, hourly lane, allowlist, reply with Joe in cc, Needs Joe outside the allowlist or on pricing, payment or vendors)
- Lane ID: pending
- Skills: intake-email (planned, queue item Q08); every reply checked with [checker v0.1](../skills/checker/SKILL.md)
- Date: 2026-10-01

## 1. Mission

Give the core team a door into PCOS without sharing any login. Read the requests
they send with the subject prefix [PCOS] (or to the shared intake mailbox). Route
each one by the kernel and answer it from PCOS sources with evidence. Prepare
the reply with Joe in cc. Anything outside the allowlist, or touching pricing,
payment, vendors or external parties, becomes a Needs Joe row instead.

Never: send while the send gate in part 4 is closed; send to anyone outside the
allowlist; make or imply a price, payment, vendor or external commitment;
forward internal files outside the company; answer from memory instead of a
source.

## 2. Inputs by ID

- L0, always loaded: [[KERNEL]].
- L1, every run: new messages in [[PCOS_INTAKE]] since the last run; the
  allowlist rule row in [[RULES]] (five addresses, named by Joe, private).
- L2, by request type: the task row in [[WORKLIST]] (order and task status);
  [[DECISIONS]] (settled answers); Live rows in [[RULES]] and [[CANON]] (rules
  are referred to, never re-priced); REFINED material in [[PCOS_KB]] and
  [[KL_DOMAINS]]; the full thread of the request (the terminal message
  controls).
- Knowledge scope: REFINED only. Requests that need RAW research become a
  Needs Joe row with the question restated.

## 3. Tools allowed

- Outlook (Microsoft 365 connector): read [[PCOS_INTAKE]]; create the reply as
  a draft on the original thread in [[MAIL_DRAFTS]] with Joe in cc. Send only
  when the send gate in part 4 is open and the requester is on the allowlist.
- Notion: one [[INBOX]] row per request (requester role, ask, route, answer
  summary, evidence, draft link, status Drafted, Sent or Needs Joe);
  [[CHANGELOG]] rows; one heartbeat in [[LANES]].
- Not allowed: send outside the gate; reply to external parties; attach files
  from Drive; change [[WORKLIST]] rows (changes go to the closeout owner as
  Inbox rows); mint Task IDs.

## 4. Rules and kernel version

- Kernel 1.0. The mismatch rule and the live-rules fallback are in
  [CARD_TEMPLATE](CARD_TEMPLATE.md).
- Laws 3, 4, 5 (no autonomous send), 6 (payment or bank changes are verified
  outside the email; credentials are never copied) and 8. The kernel routing
  section applies; drafts follow Joe's preferences in the kernel (reply on the
  original thread, signature inserted, no duplicate typed sign-off).
- Lane rules, from the dev-session record of 2026-09-27 (turn 3, decision 4,
  accepted by default by Joe): allowlist of five addresses named by Joe; reply
  with Joe in cc; Needs Joe outside the allowlist or on pricing, payment,
  vendors or external parties.
- Send gate: Law 5 forbids autonomous sends. Allowlisted sends need two things,
  both open today: the five addresses from Joe, and a Live kernel rule row that
  makes the Door 1 exception. Until both exist the lane drafts only, and Joe
  sends from Drafts.

## 5. Output contract with evidence labels

- Reply draft: short and on the original thread, Joe in cc. Each fact in the
  answer cites its source key and carries its label.
- [[INBOX]] row per request: requester (role and address), ask in one line,
  route, answer summary, evidence, draft link, status Drafted, Sent or Needs
  Joe.
- Evidence labels: facts from rows and files opened in this run are Confirmed.
  Anything not verified is Needs Source Check, and the reply says so plainly.
  Requests touching pricing, payment, vendors or external parties are Needs Joe
  Approval and get no answer beyond "Joe will reply".
- Run record: messages read, rows written, drafts created, sends (if the gate is
  open), sources opened (keys and IDs), kernel version; one heartbeat.
- Done means: every new request has an Inbox row and either a draft or a Needs
  Joe status.
- Eval: requests per week; share answered without Joe; Joe's edits to replies
  (logged in [[CORRECTIONS]]); response time. [[GOLDEN_SET]] categories
  routing and drafting.

## 6. Trigger and owner model

- Trigger: hourly on weekdays during working hours, Mexico City.
- Runs on: Claude scheduled task or a Claude Code Routine on a schedule
  (Microsoft 365 and Notion connectors).
- Model: Claude Opus answers and drafts. The checker lane checks every reply on
  a different Claude model before it reaches Drafts.
- Owner: Claude lanes. Joe names the allowlist and, while the gate is closed,
  sends.
- Escalation: Needs Joe rows appear as one card item per request in the EXO
  slots, never as a separate list.
- Depends on: PC-2 (Outlook folder and rule for the [PCOS] intake); the five
  allowlist addresses from Joe; the kernel send-exception row; build day
  ([[INBOX]], [[LANES]]); the intake-email skill (queue item Q08).

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, queue item Q01 | first card; send
gate added because Law 5 and the Door 1 design conflict until the kernel holds
the exception | register P2-09; dev-session record of 2026-09-27, turn 3 | Joe's
default acceptance 2026-09-28; PCOS_DISPATCH_2026-09-29 PROMPT C1
