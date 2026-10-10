"""Contract tests for QX30: EXO distributes front-line work through safe drafts.

The EXO lane is a prompt-driven Routine, not a Python mail client.  These tests
therefore use small mocked Outlook conversations to pin the observable policy
in the card, skill, Routine and checker: external people never receive an
internal instruction, approval never sends, and only later mail from the named
owner can answer the step.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tests.test_agents_skills import section

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "exo" / "SKILL.md"
CARD = ROOT / "agents" / "exo.md"
ROUTINE = ROOT / "routines" / "exo.md"
CHECKLISTS = ROOT / "skills" / "checker" / "references" / "checklists.md"


@dataclass(frozen=True)
class MockMessage:
    message_id: str
    conversation_id: str
    sender: str
    to: tuple[str, ...]
    cc: tuple[str, ...] = ()
    sent_at: datetime = datetime(2026, 10, 9, tzinfo=timezone.utc)
    answers_outcome: bool = False


INTERNAL = {"joe@company.test", "owner@company.test", "ops@company.test"}


def read(path):
    return path.read_text(encoding="utf-8")


def flat(text):
    return " ".join(text.split())


def safe_reply_recipients(message, intended_owner):
    """Expected recipient gate for the mocked connector response."""
    assert intended_owner in INTERNAL
    recipients = []
    for address in (*message.to, *message.cc, intended_owner):
        if address in INTERNAL and address != "joe@company.test" and address not in recipients:
            recipients.append(address)
    return tuple(recipients)


def distribution_state(*, approved, sent, replies, owner, deadline, now):
    """Expected evidence rule the prompt must state for mocked mail."""
    if not approved:
        return "Drafted"
    if sent is None:
        return "Approved"
    for reply in replies:
        if (reply.conversation_id == sent.conversation_id
                and reply.sent_at > sent.sent_at
                and reply.sender == owner
                and reply.answers_outcome):
            return "Answered"
    return "Overdue" if now > deadline else "Awaiting owner"


def test_mock_external_thread_keeps_only_the_internal_owner():
    source = MockMessage(
        "external-1", "conversation-1", "rep@vendor.test",
        ("joe@company.test",), ("owner@company.test", "buyer@customer.test"),
    )
    assert safe_reply_recipients(source, "owner@company.test") == ("owner@company.test",)

    draft = flat(section(read(SKILL), "## 8. Draft a front-line instruction"))
    checker = flat(section(read(CHECKLISTS), "## mail-draft"))
    for text in (draft, checker):
        assert "conversation ID" in text and "source message ID" in text
        assert "internal" in text and "To, Cc and Bcc" in text
        assert "representative, customer, vendor" in text
    assert "Fail closed" in draft and "write no draft" in draft


def test_mock_internal_thread_is_a_reply_not_a_new_message():
    source = MockMessage(
        "internal-1", "conversation-2", "ops@company.test",
        ("joe@company.test", "owner@company.test"),
    )
    assert safe_reply_recipients(source, "owner@company.test") == ("owner@company.test",)

    draft = flat(section(read(SKILL), "## 8. Draft a front-line instruction"))
    assert "reply on the source conversation, not a new subject" in draft
    assert "updates the same draft rather than creating a duplicate" in draft


def test_instruction_form_and_mail_style_are_fixed():
    draft = flat(section(read(SKILL), "## 8. Draft a front-line instruction"))
    for required in (
        "one to three lines", "outcome", "explicit deadline", "loop me only if",
        "greeting", "we/us voice", "[[EMAIL_RULES]]", "plain description",
        "signature `JOE BM`", "type no sign-off", "job type mail-draft", "Never send",
    ):
        assert required in draft
    assert "not ready for that draft" in flat(section(read(SKILL), "## 1. Break a task into steps"))


def test_card_has_one_tap_approve_edit_skip_and_none_sends():
    card_build = flat(section(read(SKILL), "## 2. Build a card (each slot)"))
    filing = flat(section(read(SKILL), "## 3. File the answers"))
    prompt = flat(read(ROUTINE))
    for text in (card_build, filing, prompt):
        assert "Approve" in text and "Edit" in text and "Skip" in text
    assert "Approve means the checked reply draft stays in Drafts for Joe to send; it does not send" in card_build
    assert "Edit applies only Joe's stated edit" in filing
    assert "Skip leaves it unsent" in filing and "keeps the step open" in filing
    assert "No action sends" in prompt


def test_mock_approval_waits_for_sent_evidence_then_the_named_owner():
    sent = MockMessage(
        "sent-1", "conversation-3", "joe@company.test", ("owner@company.test",),
        sent_at=datetime(2026, 10, 9, 14, tzinfo=timezone.utc),
    )
    wrong_person = MockMessage(
        "reply-1", "conversation-3", "ops@company.test", ("joe@company.test",),
        sent_at=datetime(2026, 10, 9, 15, tzinfo=timezone.utc), answers_outcome=True,
    )
    owner_reply = MockMessage(
        "reply-2", "conversation-3", "owner@company.test", ("joe@company.test",),
        sent_at=datetime(2026, 10, 9, 16, tzinfo=timezone.utc), answers_outcome=True,
    )
    deadline = datetime(2026, 10, 10, 18, tzinfo=timezone.utc)

    assert distribution_state(approved=True, sent=None, replies=(),
                              owner="owner@company.test", deadline=deadline,
                              now=datetime(2026, 10, 9, 17, tzinfo=timezone.utc)) == "Approved"
    assert distribution_state(approved=True, sent=sent, replies=(wrong_person,),
                              owner="owner@company.test", deadline=deadline,
                              now=datetime(2026, 10, 9, 17, tzinfo=timezone.utc)) == "Awaiting owner"
    assert distribution_state(approved=True, sent=sent, replies=(wrong_person, owner_reply),
                              owner="owner@company.test", deadline=deadline,
                              now=datetime(2026, 10, 9, 17, tzinfo=timezone.utc)) == "Answered"
    assert distribution_state(approved=True, sent=sent, replies=(wrong_person,),
                              owner="owner@company.test", deadline=deadline,
                              now=datetime(2026, 10, 11, tzinfo=timezone.utc)) == "Overdue"

    watch = flat(section(read(SKILL), "## 9. Watch the owner's reply"))
    for required in (
        "Approval alone is not a send", "exact draft appears in [[MAIL_SENT]]",
        "same conversation", "intended owner's address", "answers the requested outcome",
        "explicit deadline", "Distribution Overdue", "Subject match", "silence",
    ):
        assert required in watch


def test_card_routine_and_checker_all_carry_the_distribution_gate():
    card = flat(read(CARD))
    routine = flat(read(ROUTINE))
    mail_check = flat(section(read(CHECKLISTS), "## mail-draft"))
    question_check = flat(section(read(CHECKLISTS), "## question-card"))
    for text in (card, routine, mail_check):
        assert "internal" in text and "Never send" in text
        assert "JOE BM" in text and "loop me only if" in text
    assert "Approve / Edit / Skip" in question_check
    assert "leaves the draft in Drafts for Joe to send and never sends it" in question_check
