def test_normalize_phone(merger):
    """Test phone number normalization logic."""
    assert merger.normalize_phone("+1234567890") == "+1234567890"
    assert merger.normalize_phone("(123) 456-7890") == "1234567890"
    assert merger.normalize_phone("1-800-CONTACTS") == "1800"  # Letters removed
    assert merger.normalize_phone("+44 20 7123 4567") == "+442071234567"
    assert merger.normalize_phone("   555   ") == "555"


def test_normalize_email(merger):
    """Test email address normalization logic."""
    assert merger.normalize_email("test@example.com") == "test@example.com"
    assert merger.normalize_email("TEST@EXAMPLE.COM") == "test@example.com"
    assert (
        merger.normalize_email("Test.User@Example.Co.Uk") == "test.user@example.co.uk"
    )
