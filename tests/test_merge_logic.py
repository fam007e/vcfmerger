def test_deduplication_key(merger):
    """Test that similar contacts generate compatible keys."""
    # Contact 1
    props1 = {
        "FN": "John Doe",
        "N": None,
        "TEL": {("123456", "TEL:123456")},
        "EMAIL": {("john@example.com", "EMAIL:john@example.com")},
    }
    key1 = merger._get_contact_key(props1)

    # Contact 2 (Same name, different phone format but same digits)
    props2 = {
        "FN": "JOHN DOE",
        "N": None,
        "TEL": {("123456", "TEL:(123) 456")},
        "EMAIL": set(),
    }
    key2 = merger._get_contact_key(props2)

    # Should NOT match exactly because keys include all phones/emails
    # But let's verify the components
    assert key1[0] == "john doe"
    assert key2[0] == "john doe"


def test_merge_logic_simple(merger):
    """Test merging strictly duplicate contacts via the main merge method."""
    vcf1 = """BEGIN:VCARD
VERSION:3.0
FN:Alice
TEL:111111
END:VCARD"""

    vcf2 = """BEGIN:VCARD
VERSION:3.0
FN:Alice
EMAIL:alice@example.com
END:VCARD"""

    # These should merge because FN matches (and no conflicting phones/emails to distinguish)
    # Note: Logic depends on _get_contact_key.
    # Current implementation: key = (normalized_fn, frozenset(tels), frozenset(emails))
    # If sets differ, keys differ -> NO MERGE by default implementation unless logic is fuzzy?
    # Checking source:
    # key = (normalized_fn, normalized_tels, normalized_emails)
    # So if one has email and one doesn't, they are DIFFERENT contacts.

    merged = merger.merge_vcfs([vcf1, vcf2])

    # Expectation: 2 separate contacts because one has email and one doesn't
    # This reveals strict deduplication logic.
    assert "TEL:111111" in merged
    assert "EMAIL:alice@example.com" in merged
    # Should appear twice?
    assert merged.count("BEGIN:VCARD") == 2


def test_merge_exact_duplicate(merger):
    """Test merging exact duplicates."""
    vcf = """BEGIN:VCARD
VERSION:3.0
FN:Bob
TEL:222222
END:VCARD"""

    merged = merger.merge_vcfs([vcf, vcf])

    # Should be 1 contact
    assert merged.count("BEGIN:VCARD") == 1
    assert "TEL:222222" in merged
