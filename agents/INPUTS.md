# Input keys

Version v0.3, 2026-10-09.

Cards and skills name their sources as `[[KEY]]`. A key stands for exactly one
object: a Drive file or folder, a Notion database, view or page, an Outlook
folder, or this repository. An agent opens a key's object directly and never
searches for it.

A **group** is written like a key and stands for a fixed list of keys (table
"Groups" below). An agent resolves each member key to its one object and opens
each directly. One key is a set by nature: `MAIL_ROUTED`, the Outlook folders
named in `[[BRIEF_RULES]]` section A. Outlook folders are opened by exact name,
so that list is the key's object, and the agent opens every folder it names and
no other.

**IDs are not kept here.** This repository is public, and Operating Card v7.4
(WRITE PATHS) says never to put real business data in it. Each key is resolved to
its ID through the private Drive file `PCOS_AGENT_INPUT_IDS` (latest version, in
the folder `PCOS_BUILD_KIT_2026-09-28`). On build day, that table moves into the
kernel's "Where things are" block. Keeping IDs in one table also helps when a
governance file is superseded: its ID changes and only one line has to change.

If a key does not resolve, the source is Blocked for that run. The agent reports
it and does not search for a substitute.

Status: **exists** (the object exists now), **build day** (created in the phase-1
build session), **planned** (a later queue item or register entry creates it).

## Kernel and governance

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `KERNEL` | PCOS KERNEL page; until build day the draft `KERNEL_v1.0.md` in `[[BUILD_KIT]]` | Notion / Drive | Laws, routing, write rules, lane table, kernel version | exists (draft) |
| `OPERATING_CARD` | [LIVE][CORE RULES] PCOS Operating Card, latest version | Drive | Live laws, START and CLOSE steps, write paths until cutover | exists |
| `BRIEF_RULES` | PCOS_BRIEF_RULES, live version | Drive | Sweep scope, evaluation order, routes, measured owner map, draft desk | exists |
| `CANON` | [CANON] Master v1 | Drive | Business rules authority until rules become Rules rows | exists |
| `REGISTER` | PCOS_PHASE2_REGISTER, latest version | Drive | Phase-2 items P2-01 onward, with status | exists |
| `REGISTRY` | [REGISTRY] PCOS Document Registry, live version | Drive | The operating document registry: each governed document with its title, ID and status; searched before asking Joe (kernel section 2, step 4). Not `REGISTER` | exists |
| `BUILD_KIT` | PCOS_BUILD_KIT_2026-09-28 | Drive folder | Kernel draft, build material, this ID map | exists |
| `DEV_SESSIONS` | _PCOS_DEV_SESSIONS | Drive folder | Full development-session records (why each lane exists) | exists |
| `QUEUE` | _PCOS_QUEUE | Drive folder | Queue file, CLAIM, DONE and FAILED files | exists |

## State and handoff

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `NOW` | PCOS_NOW | Drive | State file; becomes a rendered mirror at cutover | exists |
| `WORKLIST` | [LIVE] PCOS Worklist, current version | Drive sheet | Task rows, the cursor (canon until cutover) | exists |
| `HUB` | PCOS v5 (sandbox) · Start here | Notion page | Hub map, write rule, database list | exists |
| `NOTION_WORKLIST` | Worklist | Notion database | Mirror of the Drive Worklist until cutover | exists |
| `DECISIONS` | Decisions | Notion database | Open and decided questions, defaults, due dates, card rows | exists |
| `RULES` | Rules | Notion database | Rules rows with stage (Live, Candidate, Retired); owner map rows | exists |
| `CHANGELOG` | Changelog | Notion database | One row per change: what, why, authority, tool, kernel version | exists |
| `CORRECTIONS` | Corrections | Notion database | Joe's edits to AI output | exists |
| `GOLDEN_SET` | Golden Set | Notion database | Past corrections used as the eval set | exists |
| `INBOX` | Inbox | Notion database | DELTA rows (source, scope, summary, why, next action, confidence, status) | build day |
| `LANES` | Lanes | Notion database | One heartbeat row per scheduled run | build day |
| `TODAY` | Today | Notion page | Rendered daily page, at most 12 lines | build day |
| `INBOX_FOLDER` | _PCOS_INBOX | Drive folder | DELTA files (fallback when a Notion write fails) | exists |
| `CHANGELOG_FOLDER` | _PCOS_CHANGELOG | Drive folder | Per-run change entries in Drive | exists |
| `ARCHIVE` | _PCOS_ARCHIVE | Drive folder | Run reports, superseded versions, snapshots | exists |

## Phase-2 databases (queue item Q03)

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `PHASE2_SCHEMA` | PCOS v5 (sandbox) · Phase 2 schema | Notion page | One line per phase-2 database | exists |
| `PREDICTION` | Prediction | Notion database | Prediction ledger rows | exists |
| `STEPS` | Steps | Notion database | EXO step rows linked to Worklist rows | exists |
| `COUNCIL` | Council | Notion database | Board-council rows | exists |
| `COUNCIL_REVIEWER_VIEW` | Council, view "Reviewer" | Notion view | Council rows without Author, Final, Dissent | exists |
| `KNOWLEDGE` | Knowledge | Notion database | Claim rows with source ID and status | exists |
| `CAPTURE` | Capture | Notion database | Voice and text dumps waiting to be parsed | exists |
| `COMMITMENTS` | Commitments | Notion database | One row per commitment in Joe's mail: deliverable, direction, counterparty, due date, thread, status, evidence (P2-31) | planned (QW21) |

## Knowledge and people

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `PCOS_KB` | PCOS_KB | Drive folder | REFINED knowledge home | exists |
| `KL_00` | KL_00_PCOS_System_and_AI | Drive folder | System and AI research (kernel K8), with RAW, REFINED and `_INDEX.md` | exists |
| `KL_01` | KL_01_Stone_and_Materials | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_02` | KL_02_Mosaic_and_Waterjet_Production | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_03` | KL_03_Pricing | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_04` | KL_04_Vendors_and_Terms | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_05` | KL_05_Logistics_and_Customs_MX_US_TR | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_06` | KL_06_Sales_and_CS | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `KL_07` | KL_07_Company_and_People | Drive folder | Domain knowledge, with RAW, REFINED and `_INDEX.md` | exists |
| `AGENT_KNOWLEDGE_LAYER` | Agent Knowledge Layer | Drive folder | Older RAW shells, to be consolidated (P2-13) | exists |
| `MAIL_MINING` | PCOS_MAIL_MINING | Drive folder | Measured mail behaviour and profiles | exists |
| `PEOPLE` | PEOPLE_PROFILES, latest version | Drive | Private people profiles; never team-facing | exists |
| `JOE_DEV_LIST` | PCOS_JOE_DEV_LIST | Drive | Joe's development list | exists |

## Groups

| Group | Member keys | What it covers |
| --- | --- | --- |
| `KL_DOMAINS` | `KL_00`, `KL_01`, `KL_02`, `KL_03`, `KL_04`, `KL_05`, `KL_06`, `KL_07` | The eight knowledge domain folders |

## Question cards

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `CAL_FOLDER` | CAL calibration-loop folder | Drive folder | CAL_STATE, CAL_LOG, card files | exists |
| `CAL_STANDARD` | CAL_CARD_STANDARD, latest version | Drive | The question-card rules for Claude and ChatGPT | exists |
| `CAL_TEMPLATE` | CAL_CARD_TEMPLATE, latest version (.html) | Drive | The card page; only its JSON block is edited | exists |

## Mail and calendar (company mailbox, Microsoft 365 connector)

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `MAIL_INBOX` | Inbox | Outlook folder | Incoming mail | exists |
| `MAIL_SENT` | Sent Items | Outlook folder | Joe's sent mail: the first evidence of what he did | exists |
| `MAIL_ROUTED` | The rule-routed per-person folders named in `[[BRIEF_RULES]]` section A (a set; see the top of this file) | Outlook folders | Mail that never reaches the Inbox | exists |
| `MAIL_DRAFTS` | Drafts | Outlook folder | Drafts only; nothing in it is sent by an agent | exists |
| `PCOS_INTAKE` | [PCOS] intake folder or shared intake mailbox | Outlook | Team requests for Door 1 (P2-09) | planned (PC-2) |
| `CALENDAR` | Calendar | Outlook | Meetings, used to time cards (P2-26) | exists, not used yet |

## Code

| Key | Object (exact title or name) | System | What it holds | Status |
| --- | --- | --- | --- | --- |
| `REPO` | joedemircan3-a11y/pcos_tools | GitHub (public) | pcos_tools, these cards and skills | exists |

## Change note

v0.1 | 2026-10-01 | Claude Code on the web, PCOS queue item Q01 | first key table,
46 keys | the cards need inputs by ID and the repository is public; keys here,
IDs in the private map | PCOS_DISPATCH_2026-09-29 PROMPT C1; Operating Card v7.4
WRITE PATHS

v0.2 | 2026-10-06 | Claude Code on the web, PCOS queue item QC18 | one key per
domain folder (`KL_00` to `KL_07`, all existing since queue item Q02 and PC-1);
`KL_DOMAINS` is now a group of those keys; `MAIL_ROUTED` documented as the one
set | `KL_DOMAINS` named eight folders, so it could not resolve to the one ID that
the key contract promises (Codex review of PR 1); the kernel 1.1 key map already
lists the eight folder IDs under `KL_DOMAINS` | PCOS QUEUE_v4 item QC18

v0.3 | 2026-10-09 | Claude Code on the web, PCOS queue item QC24 | `REGISTRY`
(exists; in the kernel key map since kernel 1.2) and `COMMITMENTS` (planned; queue
item QW21 creates the database) | the cards that ask Joe search the registry first
(kernel 1.2 section 2 step 4; QK23 open point), and the Commitments lane (P2-31)
writes its own database | PCOS QUEUE_v6 item QC24, QUEUE_v7 amendment
