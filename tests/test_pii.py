from app.pii import scrub_text
from app.logging_config import scrub_event


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_passport_vn() -> None:
    out = scrub_text("Passport number: B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT_VN" in out


def test_scrub_address_vn() -> None:
    out = scrub_text("Giao hang toi so nha 12 Nguyen Trai, ho tro them")
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Card: 4111 1111 1111 1111")
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD: 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_event_redacts_all_string_fields_including_error_detail() -> None:
    event_dict = {
        "event": "request_failed",
        "payload": {
            "detail": "ValueError raised for student@vinuni.edu.vn",
            "message_preview": "Contact 0901234567",
        },
    }
    out = scrub_event(None, "error", event_dict)
    assert "student@" not in out["payload"]["detail"]
    assert "REDACTED_EMAIL" in out["payload"]["detail"]
    assert "0901234567" not in out["payload"]["message_preview"]
    assert "REDACTED_PHONE_VN" in out["payload"]["message_preview"]
