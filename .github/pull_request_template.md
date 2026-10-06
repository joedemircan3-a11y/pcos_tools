## What and why

<!-- One or two sentences: what this pull request changes, which PCOS queue item or register entry (P2-NN) asked for it, and why. -->

## Files

<!-- The paths added or changed, one line each. -->

## Review checklist

Tick each item, or write why it does not apply. This repository is **public**.

- [ ] **Six-part card present.** Every new or changed card in `agents/` keeps the six parts in order: Mission; Inputs by ID; Tools allowed; Rules and kernel version; Output contract with evidence labels; Trigger and owner model. The version is bumped and the change note updated.
- [ ] **Sources by ID.** Every source is named by an input key (`[[KEY]]`) that is defined in `agents/INPUTS.md`, and resolves through the private ID map. No source is described vaguely ("the sheet", "the latest file"), and no raw Drive or Notion ID appears.
- [ ] **Evidence labels.** Every claim in a card, skill, prompt or council draft carries one of the six Law 4 labels: Confirmed, Candidate, Needs Source Check, Needs Thread Check, Needs Joe Approval, Blocked.
- [ ] **No pricing commitment.** Nothing sets, quotes, changes or implies a price, discount, payment or vendor term. Pricing logic refers to rule rows; it never restates their values.
- [ ] **No external send.** Nothing sends mail or messages, posts outside this repository or shares a file. Drafts stay drafts; any send needs a Live kernel rule and Joe's approval.
- [ ] **No business data.** No Drive or Notion ID or link, no person's name or address, no customer, vendor term, price or mail text. `tests/test_agents_skills.py` checks the patterns it can.
- [ ] **Tests pass.** `python -m pytest -q`

## Notes for reviewers

<!-- Open questions, Candidates with their defaults, anything a reviewer should check first. -->
